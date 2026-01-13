#!/usr/bin/env python3
"""Pre-tokenize dataset for faster training."""

import argparse
from pathlib import Path

from datasets import load_dataset
from transformers import AutoTokenizer
from rich.console import Console
from omegaconf import OmegaConf

console = Console()


def tokenize_dataset(config_path: str = "configs/train.yaml", output_dir: str = "data/tokenized"):
    """Pre-tokenize dataset and save to disk.

    Args:
        config_path: Path to training config
        output_dir: Output directory for tokenized data
    """
    console.rule("[bold cyan]Dataset Tokenization")

    # Load config
    cfg = OmegaConf.load(config_path)
    console.print(f"[cyan]Config:[/cyan] {config_path}")
    console.print(f"[cyan]Model:[/cyan] {cfg.model_name}")

    # Load tokenizer
    console.print(f"[yellow]Loading tokenizer from {cfg.model_name}...[/yellow]")
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load dataset
    console.print(f"[yellow]Loading dataset from {cfg.dataset_path}...[/yellow]")
    data_files = list(Path(cfg.dataset_path).glob(cfg.dataset_pattern))
    console.print(f"[green]Found {len(data_files)} files[/green]")

    dataset = load_dataset(
        "json",
        data_files=[str(f) for f in data_files],
        split="train"
    )
    console.print(f"[green]Loaded {len(dataset)} samples[/green]")

    # Tokenize function
    def _extract_field(example, keys):
        for key in keys:
            value = example.get(key)
            if value:
                return value
        return ""

    def tokenize(example):
        # Handle pre-formatted text (from messages format loader)
        if "text" in example:
            text = example["text"]
            # Can't separate prompt/completion from pre-formatted text
            # Tokenize and mask only padding
            tokenized = tokenizer(
                text,
                truncation=True,
                max_length=cfg.max_length,
                padding="max_length",
            )
            labels = tokenized["input_ids"][:]
            pad_id = tokenizer.pad_token_id
            labels = [-100 if token == pad_id else token for token in labels]
            tokenized["labels"] = labels
            return tokenized

        # Original prompt/completion format - tokenize separately for perfect alignment
        prompt = example.get("prompt", "")
        if not prompt:
            instruction = _extract_field(example, ("instruction",))
            input_field = example.get("input", "")
            prompt = instruction if not input_field else f"{instruction}\n\n{input_field}"
        completion = _extract_field(example, ("completion", "output", "response"))

        # Tokenize prompt and completion separately (no special tokens)
        prompt_ids = tokenizer(
            prompt + "\n",
            truncation=False,
            add_special_tokens=False,
        )["input_ids"]

        completion_ids = tokenizer(
            completion,
            truncation=False,
            add_special_tokens=False,
        )["input_ids"]

        # Build input_ids manually
        input_ids = []
        if tokenizer.bos_token_id is not None:
            input_ids.append(tokenizer.bos_token_id)

        prompt_start = len(input_ids)  # where prompt begins
        input_ids.extend(prompt_ids)

        completion_start = len(input_ids)  # where completion begins
        input_ids.extend(completion_ids)

        # Build labels (mask prompt AND BOS)
        labels = [-100] * completion_start + completion_ids[:]

        # Optionally append EOS (LEARN it so model knows when to stop!)
        if tokenizer.eos_token_id is not None:
            input_ids.append(tokenizer.eos_token_id)
            labels.append(tokenizer.eos_token_id)  # Learn EOS token!

        # Truncate both input_ids AND labels together
        input_ids = input_ids[:cfg.max_length]
        labels = labels[:cfg.max_length]

        # Pad
        pad_id = tokenizer.pad_token_id
        attention_mask = [1] * len(input_ids)

        while len(input_ids) < cfg.max_length:
            input_ids.append(pad_id)
            labels.append(-100)
            attention_mask.append(0)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }

    # Tokenize with multiprocessing
    console.print(f"[yellow]Tokenizing dataset (using all CPU cores)...[/yellow]")
    tokenized = dataset.map(
        tokenize,
        batched=False,
        num_proc=None,  # Use all available cores
        desc="Tokenizing"
    )

    # Save to disk
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    console.print(f"[yellow]Saving to {output_path}...[/yellow]")
    tokenized.save_to_disk(output_path)

    console.print(f"[green]Tokenized dataset saved to:[/green] {output_path}")
    console.print(f"[cyan]Update your config:[/cyan] dataset_path: {output_dir}")
    console.rule("[bold cyan]Tokenization Complete")

    return True


def main():
    parser = argparse.ArgumentParser(description="Pre-tokenize dataset")
    parser.add_argument(
        "-c", "--config",
        default="configs/train.yaml",
        help="Path to training config (default: configs/train.yaml)"
    )
    parser.add_argument(
        "-o", "--output",
        default="data/tokenized",
        help="Output directory (default: data/tokenized)"
    )

    args = parser.parse_args()
    success = tokenize_dataset(args.config, args.output)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
