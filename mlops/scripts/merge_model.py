#!/usr/bin/env python3
"""Merge LoRA adapter into base model for deployment."""

import argparse
from pathlib import Path

import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from rich.console import Console
import inspect

console = Console()


def merge_model(adapter_path: str, output_path: str = None, cuda_device: str = "0"):
    """Merge LoRA adapter with base model.

    Args:
        adapter_path: Path to the LoRA adapter (e.g., outputs/runs/latest/model)
        output_path: Path for merged model output (default: outputs/runs/latest/merged)
        cuda_device: CUDA device to use (default: "0")
    """
    adapter_path = Path(adapter_path)

    if not adapter_path.exists():
        console.print(f"[red]Adapter path not found:[/red] {adapter_path}")
        return False

    # Default output path
    if output_path is None:
        output_path = adapter_path.parent / "merged"
    output_path = Path(output_path)

    console.rule("[bold cyan]Merging LoRA Adapter")

    # Load adapter config to get base model name
    console.print(f"[cyan]Loading adapter config from:[/cyan] {adapter_path}")
    peft_config = PeftConfig.from_pretrained(adapter_path)
    base_model_name = peft_config.base_model_name_or_path
    console.print(f"[cyan]Base model:[/cyan] {base_model_name}")

    # Load base model on specified CUDA device
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = cuda_device
    console.print(f"[yellow]Loading base model on CUDA:{cuda_device}...[/yellow]")
    dtype_param = "dtype" if "dtype" in inspect.signature(AutoModelForCausalLM.from_pretrained).parameters else "torch_dtype"
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        **{dtype_param: torch.bfloat16},
        device_map="auto",
        trust_remote_code=True,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)

    # Load and merge adapter
    console.print("[yellow]Loading and merging adapter...[/yellow]")
    model = PeftModel.from_pretrained(base_model, adapter_path)
    merged_model = model.merge_and_unload()

    # Save merged model
    console.print(f"[yellow]Saving merged model to:[/yellow] {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    merged_model.save_pretrained(output_path, safe_serialization=True)
    tokenizer.save_pretrained(output_path)

    console.print(f"[green]Merged model saved to:[/green] {output_path}")
    console.rule("[bold cyan]Merge Complete")

    return True


def main():
    parser = argparse.ArgumentParser(description="Merge LoRA adapter into base model")
    parser.add_argument(
        "adapter_path",
        nargs="?",
        default="outputs/runs/latest/model",
        help="Path to LoRA adapter (default: outputs/runs/latest/model)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output path for merged model (default: outputs/runs/latest/merged)"
    )
    parser.add_argument(
        "--cuda", "-c",
        default="0",
        help="CUDA device to use (default: 0)"
    )

    args = parser.parse_args()
    success = merge_model(args.adapter_path, args.output, args.cuda)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
