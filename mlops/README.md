# LLM Fine-Tuning MLOps Pipeline

A production-ready MLOps pipeline for fine-tuning Large Language Models using LoRA (Low-Rank Adaptation) with comprehensive experiment tracking, evaluation, and deployment capabilities.

## Features

- **LoRA Fine-Tuning** - Memory-efficient fine-tuning using PEFT
- **Flexible Data Formats** - Supports both chat/messages and prompt/completion formats
- **Experiment Tracking** - Timestamped runs with config snapshots and TensorBoard logging
- **Model Evaluation** - Comprehensive metrics (ROUGE, BLEU, exact match, Jaccard overlap)
- **Baseline Comparison** - Compare fine-tuned models against base models
- **HuggingFace Integration** - One-command push to HuggingFace Hub
- **Remote Training** - SSH-based training on GPU servers
- **Data Versioning** - Optional LakeFS integration for data lineage

## Quick Start

```bash
# 1. Setup
make venv && source .venv/bin/activate
make install

# 2. Prepare data (if using ChatGPT export format)
make convert

# 3. Train
make train

# 4. Evaluate
make eval

# 5. Compare with baseline
make eval-baseline

# 6. Publish (if model improves over baseline)
make publish-hf
```

## Project Structure

```
.
├── configs/                    # Hydra configuration files
│   ├── train.yaml             # Training configuration
│   ├── eval.yaml              # Evaluation configuration
│   └── eval_baseline.yaml     # Baseline model evaluation
├── data/                       # Training and evaluation data
│   ├── *.jsonl                # Training data files
│   └── eval/                  # Evaluation data
│       ├── test.jsonl
│       ├── dev.jsonl
│       └── adversarial.jsonl
├── src/                        # Source code
│   ├── main.py                # CLI entry point
│   ├── train/
│   │   └── pipeline.py        # Training orchestration
│   ├── eval/
│   │   └── evaluator.py       # Evaluation framework
│   ├── data/
│   │   ├── loader.py          # Dataset loading
│   │   └── sources.py         # Data source abstraction
│   ├── deploy/
│   │   └── push.py            # Model publishing
│   └── utils/
│       └── environment.py     # Environment detection
├── scripts/
│   └── convert_data.py        # Data format conversion
├── outputs/                    # Training outputs
│   └── runs/
│       ├── 2024-01-15_10-30-45/
│       │   ├── model/         # Saved model + tokenizer
│       │   ├── config_used.yaml
│       │   ├── metrics.json
│       │   └── logs/          # TensorBoard logs
│       └── latest -> ...      # Symlink to latest run
├── artifacts/                  # Evaluation artifacts
│   └── metrics/
├── Makefile                    # Command shortcuts
└── requirements.txt            # Python dependencies
```

## Configuration

### Training Configuration (`configs/train.yaml`)

```yaml
# Model
model_name: meta-llama/Meta-Llama-3-8B

# Data
dataset_path: ./data
dataset_pattern: "*.jsonl"
data_format: messages  # "messages" or "prompt_completion"

# Data Source
data_source:
  type: local  # "local" or "lakefs"

# Training Hyperparameters
epochs: 16
batch_size: 8
lr: 0.0025
max_length: 512
gradient_accumulation_steps: 4

# Learning Rate Schedule
warmup_ratio: 0.03
weight_decay: 0
lr_scheduler_type: cosine  # "linear", "cosine", "constant"

# Precision
bf16: true  # Use bfloat16 (recommended for modern GPUs)

# LoRA Configuration (High-Capacity for Custom DSL Learning)
lora_r: 64
lora_alpha: 128
lora_dropout: 0.05
lora_target_modules:  # Full coverage for maximum learning capacity
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj

# Memory Optimization
gradient_checkpointing: true

# Hardware
cuda_visible_devices: "0"
```

### Key Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `model_name` | HuggingFace model ID | `meta-llama/Meta-Llama-3-8B`, `codellama/CodeLlama-7b-Instruct-hf` |
| `data_format` | Input data format | `messages` or `prompt_completion` |
| `epochs` | Training epochs | 8-16 (watch for overfitting) |
| `lr` | Learning rate | 1e-4 to 3e-3 for LoRA |
| `max_length` | Max sequence length | 256, 384, 512 |

### Learning Rate Schedule

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `warmup_ratio` | Fraction of steps for LR warmup | 0.03 - 0.1 |
| `weight_decay` | L2 regularization | 0 - 0.01 |
| `lr_scheduler_type` | LR decay schedule | `linear`, `cosine`, `constant` |

### LoRA Configuration

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| `lora_r` | LoRA rank (capacity) | 16 (standard), 64 (high-capacity) |
| `lora_alpha` | LoRA scaling factor | Usually 2x `lora_r` |
| `lora_dropout` | Dropout for regularization | 0.05 - 0.1 |
| `lora_target_modules` | Layers to apply LoRA | See below |

**Target Modules Options:**

```yaml
# Minimal (attention only) - faster, less memory
lora_target_modules:
  - q_proj
  - v_proj

# Full coverage (attention + MLP) - maximum learning capacity
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj
```

### Precision Settings

| Parameter | Description | When to Use |
|-----------|-------------|-------------|
| `bf16: true` | BFloat16 precision | Modern GPUs (A100, RTX 30xx+) |
| `bf16: false` | FP16 precision | Older GPUs |
| `gradient_checkpointing` | Trade compute for memory | Limited VRAM |

## Data Formats

### Messages Format (Chat/Conversational)

```json
{"messages": [
  {"role": "user", "content": "What is FLOWROLL?"},
  {"role": "assistant", "content": "FLOWROLL is a rolling aggregation function..."},
  {"role": "user", "content": "How do I use it?"},
  {"role": "assistant", "content": "Use FLOWROLL(Value, PeriodCount, Direction)..."}
]}
```

### Prompt/Completion Format

```json
{"prompt": "What is FLOWROLL?", "completion": "FLOWROLL is a rolling aggregation function..."}
```

### Instruction Format (Alternative)

```json
{"instruction": "Explain FLOWROLL", "input": "", "output": "FLOWROLL is..."}
```

### Converting ChatGPT Exports

If your data is in multi-line JSON format (ChatGPT export style):

```bash
make convert
```

This automatically converts multi-line JSON to single-line JSONL while skipping already-valid files.

## Training

### Local Training

```bash
# Using default config
make train

# Using custom config
make train TRAIN_CONFIG=train_custom
```

### Remote Training (GPU Server)

```bash
# One-time setup
make push        # Sync code to remote
make ssh-init    # Initialize remote environment

# Training
make ssh-train   # Run training on GPU server
```

### Monitoring Training

Training metrics are logged to TensorBoard:

```bash
tensorboard --logdir outputs/runs/latest/logs
```

**Healthy training signs:**
- Loss decreasing steadily
- Grad norm stable (slight increase is normal)
- No sudden spikes

**Example output:**
```
{'loss': 2.73, 'epoch': 0.25}  # Starting loss
{'loss': 1.55, 'epoch': 1.0}   # Decreasing
{'loss': 0.95, 'epoch': 4.0}   # Good progress
{'loss': 0.61, 'epoch': 5.5}   # Consider stopping if plateauing
```

### Memory Optimization

For limited GPU memory:

| Setting | Effect |
|---------|--------|
| `gradient_checkpointing: true` | Trades compute for memory |
| `bf16: true` | Uses less memory than FP32 |
| `batch_size: 1` | Minimum memory usage |
| `gradient_accumulation_steps: 4+` | Effective larger batch |
| `lora_r: 16` (vs 64) | Fewer trainable parameters |
| `lora_target_modules: [q_proj, v_proj]` | Minimal LoRA coverage |
| `max_length: 256` | Shorter sequences |
| Use 7B/8B model instead of 13B | ~50% less VRAM |

**Approximate VRAM Usage (8B model):**

| Configuration | VRAM |
|---------------|------|
| Base (no LoRA) | ~16GB |
| LoRA r=16, minimal modules | ~20GB |
| LoRA r=64, full modules | ~30GB |
| + batch_size=8, max_length=512 | ~40GB |

## Evaluation

### Evaluate Fine-Tuned Model

```bash
make eval                    # Local
make ssh-eval                # Remote
```

### Evaluate Baseline Model

```bash
make eval-baseline           # Local
make ssh-eval-baseline       # Remote
```

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| `exact_match` | Percentage of perfect matches |
| `avg_jaccard_overlap` | Token-level similarity |
| `rouge1` / `rouge2` / `rougeL` | N-gram overlap scores |
| `bleu` | Precision-based translation metric |

### Evaluation Data Format

Evaluation data must be in `prompt/completion` format:

```json
{"prompt": "Your question here?", "completion": "Expected answer"}
```

Place files in `./data/eval/`:
```
data/eval/
├── test.jsonl
├── dev.jsonl
└── adversarial.jsonl
```

## Publishing

### Local Artifacts

```bash
make publish
```

Copies model to `artifacts/models/`.

### HuggingFace Hub

```bash
# Set credentials
export HF_TOKEN="hf_xxxxxxxxxxxxx"
export HF_REPO_ID="username/model-name"

# Push
make publish-hf
```

Or specify repo directly:

```bash
python -m src.main publish-hf --repo username/my-model --public
```

## MLOps Workflow

### Development Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│   │  Prepare │───▶│  Train   │───▶│ Evaluate │───▶│  Deploy  │ │
│   │   Data   │    │  Model   │    │  Model   │    │  Model   │ │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│        │               │               │               │        │
│        ▼               ▼               ▼               ▼        │
│   make convert    make train     make eval      make publish-hf│
│                                  make eval-baseline             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Comparison Workflow

1. **Train** a new model version
2. **Evaluate** the fine-tuned model on test set
3. **Evaluate baseline** (original model) on same test set
4. **Compare metrics** - if fine-tuned > baseline:
   - Push to HuggingFace
   - Update baseline reference
5. **Iterate** with new data or hyperparameters

### Output Artifacts

Each training run produces:

```
outputs/runs/2024-01-15_10-30-45/
├── model/                    # Fine-tuned model weights
│   ├── adapter_config.json   # LoRA configuration
│   ├── adapter_model.safetensors
│   ├── tokenizer.json
│   └── ...
├── config_used.yaml          # Exact config snapshot
├── metrics.json              # Evaluation metrics
└── logs/                     # TensorBoard logs
```

## CLI Reference

```bash
# Training
python -m src.main train [--config-name CONFIG]

# Evaluation
python -m src.main eval [--config-name CONFIG]

# Publishing
python -m src.main publish [MODEL_PATH]
python -m src.main publish-hf [MODEL_PATH] [--repo REPO_ID] [--public]

# Utilities
python -m src.main list-configs
python -m src.main version
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make venv` | Create virtual environment |
| `make install` | Install dependencies |
| `make convert` | Convert ChatGPT format to JSONL |
| `make train` | Run training locally |
| `make eval` | Evaluate fine-tuned model |
| `make eval-baseline` | Evaluate baseline model |
| `make publish` | Copy model to local artifacts |
| `make publish-hf` | Push model to HuggingFace Hub |
| `make push` | Sync code to remote GPU server |
| `make ssh-init` | Initialize remote environment |
| `make ssh-train` | Run training on remote |
| `make ssh-eval` | Run evaluation on remote |
| `make clean` | Remove caches and outputs |

## Environment Variables

### Required for HuggingFace Publishing

```bash
# HuggingFace Hub authentication
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"

# Target repository for model publishing
export HF_REPO_ID="your-username/your-model-name"
```

### Optional: GPU & Cache Configuration

```bash
# Select specific GPU(s) - defaults to "0"
export CUDA_VISIBLE_DEVICES="0"

# HuggingFace cache directory (for downloaded models)
export HF_HOME="/path/to/cache"
# or legacy variable
export TRANSFORMERS_CACHE="/path/to/cache"
```

### Optional: Remote Training (SSH)

Configure in `Makefile` or as environment variables:

```bash
# Remote GPU server credentials
export REMOTE_USER="username"
export REMOTE_HOST="192.168.1.100"
export REMOTE_DIR="~/Dev/my-project"
```

### Optional: LakeFS Data Versioning

```bash
# LakeFS server connection
export LAKEFS_ENDPOINT="http://localhost:8000"
export LAKEFS_ACCESS_KEY="your-access-key"
export LAKEFS_SECRET_KEY="your-secret-key"
```

### Quick Setup Script

Create a `.env` file (do not commit to git):

```bash
# .env
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"
export HF_REPO_ID="your-username/your-model-name"
export CUDA_VISIBLE_DEVICES="0"
export HF_HOME="~/.cache/huggingface"
```

Load before running:

```bash
source .env
make train
```

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | For publishing | HuggingFace API token ([get one here](https://huggingface.co/settings/tokens)) |
| `HF_REPO_ID` | For publishing | Target repo (e.g., `username/model-name`) |
| `CUDA_VISIBLE_DEVICES` | No | GPU selection (default: `0`) |
| `HF_HOME` | No | Model cache directory |
| `TRANSFORMERS_CACHE` | No | Legacy cache variable |
| `REMOTE_USER` | For SSH training | SSH username |
| `REMOTE_HOST` | For SSH training | GPU server IP/hostname |
| `REMOTE_DIR` | For SSH training | Remote project directory |
| `LAKEFS_ENDPOINT` | For LakeFS | LakeFS server URL |
| `LAKEFS_ACCESS_KEY` | For LakeFS | LakeFS access key |
| `LAKEFS_SECRET_KEY` | For LakeFS | LakeFS secret key |

## Requirements

- Python 3.10+
- CUDA-compatible GPU (recommended: 24GB+ VRAM for 7B models)
- Dependencies: PyTorch, Transformers, PEFT, Datasets, Hydra

## License

MIT License
