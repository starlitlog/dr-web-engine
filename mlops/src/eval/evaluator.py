import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Union

import torch
from rich.console import Console
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM, PeftConfig, PeftModel
from omegaconf import OmegaConf
import evaluate

try:
    from torch.utils.tensorboard import SummaryWriter
except ImportError:
    SummaryWriter = None

from src.data.loader import load_jsonl_dataset

console = Console()


# -------------------------------------------------------------------------
# Logging helpers
# -------------------------------------------------------------------------

def _log_params(cfg, keys: Iterable[str], title: str):
    data = OmegaConf.to_container(cfg, resolve=True)
    console.print(f"[bold cyan]{title}[/bold cyan]")
    for key in keys:
        value = data.get(key)
        if value is not None:
            console.print(f"  - {key}: {value}")


def _maybe_hf_repo(path: Union[str, Path]) -> bool:
    if not isinstance(path, str):
        return False
    return "/" in path and not Path(path).expanduser().exists()


def _resolve_model_path(path: Union[str, Path]) -> Union[str, Path]:
    """Ensure model path exists or fall back to latest run."""
    if _maybe_hf_repo(path):
        return path

    expanded = Path(path).expanduser()
    if expanded.exists():
        return expanded

    runs_root = expanded.parent.parent if expanded.parts else None
    if not runs_root or not runs_root.exists():
        raise FileNotFoundError(f"Model path {expanded} not found.")

    candidates = sorted(
        [d for d in runs_root.iterdir() if d.is_dir() and (d / "model").exists()],
        key=lambda p: p.name,
    )
    if not candidates:
        raise FileNotFoundError("No completed runs found.")

    fallback = candidates[-1] / "model"
    console.print(
        f"[yellow]Warning:[/yellow] Requested model path {expanded} not found; "
        f"falling back to {fallback}"
    )
    return fallback


# -------------------------------------------------------------------------
# Build eval prompt EXACTLY like train tokenize()
# -------------------------------------------------------------------------

def build_eval_input(prompt: str, tokenizer, device, max_len: int):
    """
    Reproduce the exact prompt tokenization used in training:
    - prepend BOS (if model has it)
    - prompt + newline
    - NO special tokens
    - NO padding, truncation is manual
    """

    input_ids = []

    # 1. BOS token (train added this manually)
    if tokenizer.bos_token_id is not None:
        input_ids.append(tokenizer.bos_token_id)

    # 2. prompt + newline, no special tokens
    prompt_ids = tokenizer(
        prompt + "\n",
        add_special_tokens=False
    ).input_ids

    input_ids.extend(prompt_ids)

    # 3. manual truncation
    if len(input_ids) > max_len:
        input_ids = input_ids[-max_len:]

    # Convert to tensor
    return torch.tensor([input_ids], device=device)


# -------------------------------------------------------------------------
# Build expected + Jaccard
# -------------------------------------------------------------------------

def _build_prompt(example: Dict[str, str]) -> str:
    instruction = example.get("instruction") or example.get("prompt")
    if not instruction:
        raise KeyError("Evaluation example missing 'instruction' or 'prompt'")
    input_field = example.get("input")
    if input_field:
        return f"{instruction}\n\n{input_field}"
    return instruction


def _expected_completion(example: Dict[str, str]) -> str:
    for key in ("output", "completion", "response"):
        value = example.get(key)
        if value:
            return value.strip()
    raise KeyError("Evaluation example missing completion/response")


def _jaccard_overlap(a: str, b: str) -> float:
    a_tokens = set(a.lower().split())
    b_tokens = set(b.lower().split())
    if not a_tokens and not b_tokens:
        return 1.0
    union = a_tokens | b_tokens
    if not union:
        return 0.0
    return len(a_tokens & b_tokens) / len(union)


# -------------------------------------------------------------------------
# llama.cpp runner
# -------------------------------------------------------------------------

def _prepare_llama_cpp_cfg(cfg, max_new_tokens, temperature, top_p):
    model_path = cfg.get("gguf_model_path")
    if not model_path:
        raise ValueError("GGUF evaluation requested but gguf_model_path is not set.")

    llama_cpp_binary = cfg.get("llama_cpp_binary", "../llama.cpp/build/bin/main")
    threads = cfg.get("llama_cpp_threads", 8)
    ctx = cfg.get("llama_cpp_ctx", 4096)

    model_path = Path(model_path).expanduser()
    llama_cpp_binary = Path(llama_cpp_binary).expanduser()

    if not model_path.exists():
        raise FileNotFoundError(f"GGUF model not found at {model_path}")
    if not llama_cpp_binary.exists():
        raise FileNotFoundError(f"llama.cpp binary not found at {llama_cpp_binary}")

    return {
        "model_path": model_path,
        "binary": llama_cpp_binary,
        "threads": threads,
        "ctx": ctx,
        "max_new_tokens": max_new_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "cuda_visible_devices": cfg.get("cuda_visible_devices"),
        "gpu_layers": cfg.get("llama_cpp_gpu_layers", 0),
    }


def _generate_with_llama_cpp(prompt: str, cfg: Dict) -> str:
    cmd = [
        str(cfg["binary"]),
        "-m", str(cfg["model_path"]),
        "-p", prompt,
        "-n", str(cfg["max_new_tokens"]),
        "--temp", str(cfg["temperature"]),
        "--top-p", str(cfg["top_p"]),
        "-t", str(cfg["threads"]),
        "-c", str(cfg["ctx"]),
    ]
    gpu_layers = cfg.get("gpu_layers")
    if gpu_layers not in (None, 0):
        cmd.extend(["-ngl", str(gpu_layers)])

    try:
        env = os.environ.copy()
        if cfg.get("cuda_visible_devices") is not None:
            env["CUDA_VISIBLE_DEVICES"] = str(cfg["cuda_visible_devices"])
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"llama.cpp generation failed (exit {exc.returncode}): {exc.stderr}"
        ) from exc

    return result.stdout.strip()


# -------------------------------------------------------------------------
# Evaluation Loop
# -------------------------------------------------------------------------

def run_evaluation(cfg):
    console.rule("[bold blue]Evaluation Start")

    model_path_cfg = cfg.get("model_path", "outputs/runs/latest/model")
    model_subfolder = cfg.get("model_subfolder", None)
    dataset_path = cfg.get("dataset_path", "./data")
    dataset_pattern = cfg.get("dataset_pattern", "*.jsonl")
    metrics_dir = Path(cfg.get("metrics_dir", "artifacts/metrics"))
    max_samples = cfg.get("max_eval_samples", None)  # Fixed: use correct config key
    max_new_tokens = cfg.get("max_new_tokens", 256)
    temperature = cfg.get("temperature", 0.0)
    do_sample = cfg.get("do_sample", False)
    top_p = cfg.get("top_p", 0.9)
    use_gguf = cfg.get("use_gguf", False)

    _log_params(cfg, (
        "model_path",
        "dataset_path",
        "dataset_pattern",
        "model_subfolder",
        "max_samples",
        "max_new_tokens",
        "temperature",
        "top_p",
        "do_sample",
        "cuda_visible_devices",
        "use_gguf",
        "gguf_model_path",
        "llama_cpp_binary",
    ), "Evaluation Parameters")

    cuda_visible = cfg.get("cuda_visible_devices", None)
    if cuda_visible is not None and not use_gguf:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(cuda_visible)
        console.print(
            f"[cyan]Restricting CUDA devices to:[/cyan] {os.environ['CUDA_VISIBLE_DEVICES']}"
        )

    llama_cpp_cfg = None
    if use_gguf:
        llama_cpp_cfg = _prepare_llama_cpp_cfg(cfg, max_new_tokens, temperature, top_p)
    else:
        model_path = _resolve_model_path(model_path_cfg)
        console.print(f"[green]Evaluating model:[/green] {model_path}")

    # Load dataset
    dataset = load_jsonl_dataset(dataset_path, dataset_pattern)
    total_examples = len(dataset)

    if max_samples:
        subset_size = min(max_samples, total_examples)
        dataset = dataset.select(range(subset_size))
    else:
        subset_size = total_examples

    console.print(f"[cyan]Evaluation samples:[/cyan] {subset_size}/{total_examples}")

    # Output dir
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = metrics_dir / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    if not use_gguf:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        adapter_load_kwargs = {"device_map": "auto", "torch_dtype": dtype}

        if model_subfolder:
            adapter_load_kwargs["subfolder"] = model_subfolder

        try:
            model = AutoPeftModelForCausalLM.from_pretrained(
                model_path,
                **adapter_load_kwargs,
            )
        except Exception:
            peft_config_path = Path(model_path) / "adapter_config.json"
            if peft_config_path.exists():
                peft_config = PeftConfig.from_pretrained(
                    model_path,
                    subfolder=model_subfolder,
                )
                base_model = AutoModelForCausalLM.from_pretrained(
                    peft_config.base_model_name_or_path,
                    device_map="auto",
                    torch_dtype=dtype,
                )
                model = PeftModel.from_pretrained(
                    base_model,
                    model_path,
                    subfolder=model_subfolder,
                )
            else:
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    **adapter_load_kwargs,
                )

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

    # ---------------------------------------------------------------------
    # Evaluation Loop
    # ---------------------------------------------------------------------

    exact_matches = 0
    overlaps = []
    generations = []
    predictions = []
    references = []

    console.print("[cyan]Running model inference...[/cyan]")

    for idx, example in enumerate(dataset, start=1):
        console.print(f"[blue]Prompt {idx}/{subset_size}[/blue]")

        prompt = _build_prompt(example)
        expected = _expected_completion(example)

        # GGUF path
        if use_gguf:
            generated = _generate_with_llama_cpp(prompt, llama_cpp_cfg)

        # HF model path
        else:
            # Build eval prompt EXACTLY like training
            input_ids = build_eval_input(
                prompt,
                tokenizer,
                model.device,
                max_len=4096,
            )

            # Create attention mask (all 1s, no padding)
            attention_mask = torch.ones_like(input_ids)

            # Build generation kwargs
            gen_kwargs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "max_new_tokens": max_new_tokens,
                "pad_token_id": tokenizer.pad_token_id,
                "eos_token_id": tokenizer.eos_token_id,
            }

            # Only add sampling params if do_sample=True
            if do_sample and temperature > 0:
                gen_kwargs["do_sample"] = True
                gen_kwargs["temperature"] = temperature
                gen_kwargs["top_p"] = top_p

            with torch.no_grad():
                output = model.generate(**gen_kwargs)

            # Strip the prompt based on input length
            input_len = input_ids.shape[-1]
            gen_ids = output[0][input_len:]
            generated = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

        exact = int(generated.lower() == expected.lower())
        overlap = _jaccard_overlap(expected, generated)

        exact_matches += exact
        overlaps.append(overlap)
        generations.append({
            "prompt": prompt,
            "expected": expected,
            "prediction": generated,
            "exact_match": bool(exact),
            "overlap": overlap,
        })
        predictions.append(generated)
        references.append(expected)

    # ---------------------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------------------

    metrics = {
        "samples_evaluated": subset_size,
        "exact_match": exact_matches / subset_size if subset_size else 0.0,
        "avg_jaccard_overlap": sum(overlaps) / subset_size if subset_size else 0.0,
    }

    if subset_size:
        try:
            rouge = evaluate.load("rouge")
            rouge_scores = rouge.compute(predictions=predictions, references=references)
            metrics.update({k: rouge_scores[k] for k in rouge_scores})
        except Exception as exc:
            console.print(f"[yellow]Warning:[/yellow] Failed to compute ROUGE: {exc}")

        try:
            bleu = evaluate.load("bleu")
            bleu_scores = bleu.compute(
                predictions=predictions,
                references=[[r] for r in references],
            )
            metrics["bleu"] = bleu_scores.get("bleu", 0.0)
        except Exception as exc:
            console.print(f"[yellow]Warning:[/yellow] Failed to compute BLEU: {exc}")

    # Save metrics
    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    generations_file = out_dir / "predictions.jsonl"
    with open(generations_file, "w") as f:
        for row in generations:
            f.write(json.dumps(row) + "\n")

    console.print(f"[green]Saved evaluation metrics →[/green] {metrics_file}")
    console.print(f"[green]Saved predictions →[/green] {generations_file}")

    if SummaryWriter:
        tb_dir = out_dir / "logs"
        writer = SummaryWriter(log_dir=str(tb_dir))
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                writer.add_scalar(f"eval/{k}", v, 0)
        writer.close()
        console.print(f"[green]Logged TensorBoard scalars →[/green] {tb_dir}")

    console.rule("[bold blue]Evaluation Complete ✅")
