# WebQL MLOps Pipeline

MLOps pipeline for training Large Language Models to generate WebQL queries from natural language descriptions.

## Overview

This pipeline trains models to automatically generate DR Web Engine WebQL configurations from natural language descriptions of web scraping tasks.

**Example:**
- **Input**: "Extract product names and prices from an e-commerce site"
- **Output**: Valid WebQL JSON5 configuration with proper `@xpath`, `@fields`, etc.

## Quick Start

```bash
# 1. Setup environment
make venv && source .venv/bin/activate
make install

# 2. Train WebQL model (on GPU machine)
make train TRAIN_CONFIG=train_webql

# 3. Evaluate model
make eval EVAL_CONFIG=eval_webql

# 4. Compare with baseline
make eval EVAL_CONFIG=eval_webql_baseline

# 5. Publish if improved
make publish-hf
```

## Training Data

**Source**: DR Web Engine existing training data (345 examples across 19 files)

**Categories**:
- Basic queries (quotes, news, simple extraction)
- Advanced features (actions, conditionals, following links)
- Plugin usage (AI selector, JSON-LD, API extraction)
- Error correction and validation
- Real-world examples
- XPath patterns and optimization

**Format**: Automatically converted from instruction → prompt/completion

## Model Configuration

**Base Model**: `codellama/CodeLlama-7b-Instruct-hf`
- Optimized for code generation
- Good balance of performance and resource requirements

**Key Settings** (in `configs/train_webql.yaml`):
- `max_length: 1024` - Supports complex WebQL queries
- `epochs: 8` - More training for DSL learning
- `lr: 3e-4` - Higher learning rate for code generation
- LoRA r=64, alpha=128 - High capacity for pattern learning

## Evaluation Metrics

**Syntax Validation**:
- JSON5/YAML parse validity
- Required field presence (`@url`, `@steps`, `@xpath`, `@fields`)
- XPath syntax validation

**Semantic Metrics**:
- Exact match accuracy
- ROUGE scores (token overlap)
- BLEU scores (precision-based)
- Functional equivalence testing

## Data Structure

```
mlops/
├── configs/
│   ├── train_webql.yaml           # WebQL-specific training config
│   ├── eval_webql.yaml            # Fine-tuned model evaluation
│   └── eval_webql_baseline.yaml   # Baseline model evaluation
├── data/
│   ├── converted_webql_*.jsonl    # Training data (345 examples)
│   └── eval/                      # Evaluation splits
│       ├── test.jsonl             # Basic examples
│       ├── dev.jsonl              # Advanced examples  
│       └── adversarial.jsonl      # Error correction
└── scripts/
    └── convert_webql_format.py    # Data format conversion
```

## Training on Remote GPU

```bash
# 1. Sync to GPU server
make push

# 2. Initialize remote environment (one-time)
make ssh-init

# 3. Run training remotely
make ssh-train TRAIN_CONFIG=train_webql

# 4. Run evaluation
make ssh-eval EVAL_CONFIG=eval_webql
make ssh-eval EVAL_CONFIG=eval_webql_baseline
```

## Expected Results

**Baseline Model** (CodeLlama without fine-tuning):
- Syntax validity: ~30-40%
- Exact match: ~5-10%
- Can generate JSON but lacks WebQL DSL knowledge

**Fine-tuned Model** (Expected improvements):
- Syntax validity: ~80-90%
- Exact match: ~40-60%
- Proper WebQL structure and XPath usage
- Domain-specific pattern knowledge

## Integration with DR Web Engine

**Future Plugin**: `ai_query_generator`
```bash
# Enhanced workflow
dr-web-engine --ai-generate "extract news headlines" -o results.json
```

**Current Integration Points**:
- Use existing plugin architecture
- Extend AI selector plugin capabilities
- Add to CLI as `--ai-generate` option

## Memory Requirements

**Training (CodeLlama-7b)**:
- Minimum: 16GB VRAM (with optimizations)
- Recommended: 24GB+ VRAM
- Settings for lower VRAM in config comments

**Inference**:
- ~8GB VRAM for generation
- CPU inference possible but slower

## Troubleshooting

**Common Issues**:
1. **CUDA OOM**: Reduce `batch_size`, enable `gradient_checkpointing`
2. **Data format errors**: Ensure prompt/completion format
3. **Invalid syntax**: Check conversion script output
4. **Training stagnation**: Adjust learning rate or LoRA config

**Debug Commands**:
```bash
# Check data format
head data/converted_webql_basic_queries.jsonl

# Validate config
python -m src.main list-configs

# Test training pipeline
python -m src.main train --config-name train_webql
```

## Next Steps

1. **Train** on GPU server using provided configs
2. **Evaluate** against baseline for improvement validation  
3. **Fine-tune** hyperparameters based on results
4. **Integrate** as DR Web Engine plugin
5. **Extend** with more diverse training examples