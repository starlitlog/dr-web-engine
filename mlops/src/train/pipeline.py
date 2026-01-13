import json
import os
from datetime import datetime

# Silence tokenizers parallelism warning with DataLoader workers
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from pathlib import Path
from typing import Iterable
import inspect
import shutil

from datasets import load_dataset
from omegaconf import OmegaConf
from peft import LoraConfig, get_peft_model
from rich.console import Console
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import torch
from src.data.loader import load_jsonl_dataset
from src.data.sources import DataSourceFactory


console = Console()
_TRAINING_ARGS_PARAMS = set(inspect.signature(TrainingArguments.__init__).parameters)


def create_run_dir(base="outputs/runs"):
    """Create timestamped output folder for each run"""
    base_path = Path(base).expanduser().resolve()
    base_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = base_path / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _update_latest_symlink(run_dir: Path):
    """Point outputs/runs/latest to the most recent run directory."""
    run_dir = Path(run_dir).resolve()
    latest = run_dir.parent / "latest"
    try:
        if latest.exists() or latest.is_symlink():
            if latest.is_symlink() or latest.is_file():
                latest.unlink()
            else:
                shutil.rmtree(latest)
        latest.symlink_to(run_dir, target_is_directory=True)
    except OSError as exc:
        console.print(f"[yellow]Warning:[/yellow] unable to update latest symlink: {exc}")


def _log_params(cfg, keys: Iterable[str], title: str):
    data = OmegaConf.to_container(cfg, resolve=True)
    console.print(f"[bold cyan]{title}[/bold cyan]")
    for key in keys:
        value = data.get(key)
        if value is not None:
            console.print(f"  - {key}: {value}")


def run_training(cfg):
    """Fine-tune a model using LoRA."""
    console = Console()
    console.rule("[bold green]Training Start")

    model_name = cfg.model_name
    data_path = cfg.dataset_path
    data_pattern = cfg.get("dataset_pattern", None)
    cuda_visible = cfg.get("cuda_visible_devices")
    _log_params(
        cfg,
        (
            "model_name",
            "dataset_path",
            "dataset_pattern",
            "epochs",
            "batch_size",
            "gradient_accumulation_steps",
            "lr",
            "lora_r",
            "lora_alpha",
            "lora_dropout",
            "max_length",
            "cuda_visible_devices",
        ),
        "Training Parameters",
    )
    if cuda_visible is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(cuda_visible)
        console.print(f"[cyan]Restricting CUDA devices to:[/cyan] {os.environ['CUDA_VISIBLE_DEVICES']}")

    run_dir = create_run_dir()
    console.print(f"[green]Output dir:[/green] {run_dir}")

    # Save config snapshot
    OmegaConf.save(config=cfg, f=str(run_dir / "config_used.yaml"))
    # (run_dir / "config_used.yaml").write_text(cfg.pretty())

    # === Load dataset ===
    data_source = DataSourceFactory.create_data_source(cfg)
    dataset = data_source.load_dataset(data_pattern, config=cfg)
    console.print(f"Loaded [bold]{len(dataset)}[/bold] samples")

    # === Tokenizer ===
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def _extract_field(example, keys):
        for key in keys:
            value = example.get(key)
            if value:
                return value
        raise KeyError(f"Example missing keys {keys}")

    def tokenize(example):
        # Determine prompt + completion
        prompt = example.get("prompt")
        if prompt is None:
            instruction = _extract_field(example, ("instruction",))
            input_field = example.get("input")
            prompt = instruction if not input_field else f"{instruction}\n\n{input_field}"
        completion = _extract_field(example, ("completion", "output", "response"))

        # 1. Tokenize separately (NO special tokens)
        prompt_ids = tokenizer(prompt + "\n", add_special_tokens=False).input_ids
        completion_ids = tokenizer(completion, add_special_tokens=False).input_ids

        # 2. Build input_ids manually
        input_ids = []
        if tokenizer.bos_token_id is not None:
            input_ids.append(tokenizer.bos_token_id)

        prompt_start = len(input_ids)  # where prompt begins
        input_ids.extend(prompt_ids)

        completion_start = len(input_ids)  # where completion begins
        input_ids.extend(completion_ids)

        # 3. Build labels (mask prompt AND BOS)
        labels = [-100] * completion_start + completion_ids[:]

        # 4. Optionally append EOS (LEARN it so model knows when to stop!)
        if tokenizer.eos_token_id is not None:
            input_ids.append(tokenizer.eos_token_id)
            labels.append(tokenizer.eos_token_id)  # Learn EOS token!

        # 5. Truncate both input_ids AND labels together
        input_ids = input_ids[:cfg.max_length]
        labels = labels[:cfg.max_length]

        # 6. Pad
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

    tokenized = dataset.map(tokenize, batched=False)

    # Split into train/eval
    split = tokenized.train_test_split(test_size=0.1, seed=42)
    train_dataset = split["train"]
    eval_dataset = split["test"]

    # === Base model + LoRA ===
    # Determine dtype based on config (respect fp16/bf16 settings)
    if cfg.get("bf16", False) and torch.cuda.is_available():
        load_dtype = torch.bfloat16
    elif cfg.get("fp16", False) and torch.cuda.is_available():
        load_dtype = torch.float16
    elif torch.cuda.is_available():
        load_dtype = torch.float32
    else:
        load_dtype = torch.float32

    console.print(f"[cyan]Loading model with dtype:[/cyan] {load_dtype}")
    dtype_param = "dtype" if "dtype" in inspect.signature(AutoModelForCausalLM.from_pretrained).parameters else "torch_dtype"
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        **{dtype_param: load_dtype},
        device_map="auto",
    )

    # Enable gradient checkpointing for memory efficiency
    if cfg.get("gradient_checkpointing", False):
        base_model.gradient_checkpointing_enable()
        console.print("[cyan]Gradient checkpointing enabled[/cyan]")

    # Get target modules from config, or use default
    target_modules = cfg.get("lora_target_modules", None)
    if target_modules:
        # Convert OmegaConf list to Python list if needed
        target_modules = list(target_modules)
        console.print(f"[cyan]LoRA target modules:[/cyan] {target_modules}")

    lora_cfg = LoraConfig(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules,
    )
    model = get_peft_model(base_model, lora_cfg)
    model.print_trainable_parameters()

    # === TrainingArguments ===
    logging_strategy = cfg.get("logging_strategy", "steps")
    evaluation_strategy = cfg.get("evaluation_strategy", "steps")

    # Precision settings
    use_bf16 = cfg.get("bf16", False) and torch.cuda.is_available()
    use_fp16 = not use_bf16 and torch.cuda.is_available()

    args_kwargs = dict(
        output_dir=str(run_dir),
        logging_dir=str(run_dir / "logs"),
        num_train_epochs=cfg.epochs,
        per_device_train_batch_size=cfg.batch_size,
        learning_rate=cfg.lr,
        gradient_accumulation_steps=cfg.get("gradient_accumulation_steps", 1),
        fp16=use_fp16,
        bf16=use_bf16,
        logging_steps=cfg.logging_steps,
        report_to=["tensorboard"],
        gradient_checkpointing=cfg.get("gradient_checkpointing", False),
        warmup_ratio=cfg.get("warmup_ratio", 0.0),
        weight_decay=cfg.get("weight_decay", 0.0),
        lr_scheduler_type=cfg.get("lr_scheduler_type", "linear"),
        # DataLoader optimization
        dataloader_num_workers=cfg.get("dataloader_num_workers", 4),
        dataloader_pin_memory=True,
        dataloader_prefetch_factor=cfg.get("dataloader_prefetch_factor", 2),
    )
    # Backwards-compatible handling for older Transformers versions
    if "save_strategy" in _TRAINING_ARGS_PARAMS:
        args_kwargs["save_strategy"] = "epoch"
    if "logging_strategy" in _TRAINING_ARGS_PARAMS:
        args_kwargs["logging_strategy"] = logging_strategy
    if "evaluation_strategy" in _TRAINING_ARGS_PARAMS:
        args_kwargs["evaluation_strategy"] = evaluation_strategy
    elif "evaluate_during_training" in _TRAINING_ARGS_PARAMS:
        args_kwargs["evaluate_during_training"] = True
        args_kwargs["eval_steps"] = cfg.logging_steps

    args = TrainingArguments(**args_kwargs)

    # === Trainer ===
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,  # Changed from tokenizer= to avoid deprecation warning
    )

    console.print("[yellow]Starting training...[/yellow]")
    trainer.train()

    # Save model + tokenizer
    model_dir = run_dir / "model"
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    console.print(f"[green]Saved model →[/green] {model_dir}")

    # Save metrics
    metrics = trainer.evaluate()
    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    console.print(f"[green]Saved metrics →[/green] {run_dir/'metrics.json'}")

    _update_latest_symlink(run_dir)
    console.print(f"[cyan]Updated latest run pointer →[/cyan] {run_dir}")

    console.rule("[bold green]Training Complete ✅")
