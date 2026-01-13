# WebQL Training Configuration Guide

## Training Strategy Configs

### 🚀 **Quick Testing** (`train_webql_tiny.yaml`)
**Use for**: Pipeline validation, debugging, rapid iteration
- **Model**: DialoGPT-medium (355M params)
- **Data**: 10 basic examples only
- **Time**: 2-3 minutes
- **Purpose**: Verify setup works before longer runs

```bash
make train TRAIN_CONFIG=train_webql_tiny
```

### ⚡ **Fast Iteration** (`train_webql_fast.yaml`)  
**Use for**: Quick experiments, hyperparameter testing
- **Model**: DialoGPT-small (117M params)
- **Data**: Basic queries (10 examples)
- **Time**: 5-10 minutes
- **Purpose**: Rapid feedback on approach

```bash
make train TRAIN_CONFIG=train_webql_fast
```

### 📈 **Incremental Learning** (`train_webql_incremental.yaml`)
**Use for**: Smart progression from simple to complex
- **Model**: Llama-3.2-1B-Instruct (1B params)
- **Data**: Progressive (start with 10, scale up)
- **Time**: 30-45 minutes per stage
- **Purpose**: Build confidence before full training

```bash
make train TRAIN_CONFIG=train_webql_incremental
```

### 🎯 **Production Ready** (`train_webql_llama3b.yaml`)
**Use for**: Balanced performance and training time
- **Model**: Llama-3.2-3B-Instruct (3B params) 
- **Data**: Full dataset (345 examples)
- **Time**: 1-2 hours
- **Purpose**: Good baseline for real usage

```bash
make train TRAIN_CONFIG=train_webql_llama3b
```

### 🔥 **Original Heavy** (`train_webql.yaml`)
**Use for**: Maximum capability (currently running)
- **Model**: CodeLlama-7b-Instruct (7B params)
- **Data**: Full dataset (345 examples) 
- **Time**: 4+ hours
- **Purpose**: Best possible results (if patient)

```bash
make train TRAIN_CONFIG=train_webql  # Currently running
```

## Recommended Workflow

### 1. **Start with Tiny** (2 mins)
```bash
make train TRAIN_CONFIG=train_webql_tiny
```
**Validates**: Pipeline works, no errors, basic syntax generation

### 2. **Move to Incremental** (45 mins total)
```bash
# Stage 1: Basic patterns
make train TRAIN_CONFIG=train_webql_incremental

# Stage 2: Edit config to add more data files
# Stage 3: Edit config for full dataset  
```
**Validates**: Progressive learning, model capability, WebQL understanding

### 3. **Scale to Production** (2 hours)
```bash
make train TRAIN_CONFIG=train_webql_llama3b
```
**Delivers**: Usable model with good performance

### 4. **Optimize if Needed** (4+ hours)
```bash
make train TRAIN_CONFIG=train_webql  # Heavy config
```
**Delivers**: Maximum capability model

## Model Comparison

| Config | Model Size | Training Time | VRAM | Best For |
|--------|------------|---------------|------|----------|
| `tiny` | 355M | 2-3 mins | ~2GB | Pipeline testing |
| `fast` | 117M | 5-10 mins | ~2GB | Quick experiments |
| `incremental` | 1B | 30-45 mins | ~6GB | Progressive learning |
| `llama3b` | 3B | 1-2 hours | ~12GB | Production baseline |
| `webql` | 7B | 4+ hours | ~24GB | Maximum capability |

## Configuration Philosophy

### **Problems with Original Config**:
- ❌ **CodeLlama**: Rigid, poor adaptation to new domains
- ❌ **7B Model**: Slow training, high resource requirements  
- ❌ **8 Epochs**: Long training before seeing results
- ❌ **Full Dataset**: No gradual validation

### **New Approach Benefits**:
- ✅ **Modern Models**: Llama-3.2 series more flexible
- ✅ **Progressive Sizing**: Start small, validate, scale up
- ✅ **Fast Feedback**: See results in minutes, not hours
- ✅ **Incremental Data**: Build confidence gradually

## Quick Start Recommendations

**For immediate testing**:
```bash
make train TRAIN_CONFIG=train_webql_tiny    # 2 mins
make eval EVAL_CONFIG=eval_webql             # Validate output
```

**For serious development**:
```bash
make train TRAIN_CONFIG=train_webql_llama3b  # 1-2 hours  
make eval EVAL_CONFIG=eval_webql             # Full evaluation
```

**For maximum results** (after validating approach):
```bash
make train TRAIN_CONFIG=train_webql          # 4+ hours
make eval EVAL_CONFIG=eval_webql             # Best performance
```

## Troubleshooting

**Training too slow?** → Use `tiny` or `fast` configs
**Model not learning?** → Try `incremental` approach
**Out of memory?** → Reduce `batch_size` or use smaller model
**Poor results?** → Increase model size or training time

## Next Steps

1. **Test pipeline**: `make train TRAIN_CONFIG=train_webql_tiny`
2. **Validate approach**: `make train TRAIN_CONFIG=train_webql_incremental`  
3. **Production training**: `make train TRAIN_CONFIG=train_webql_llama3b`
4. **Compare with running CodeLlama**: Evaluate both for best approach