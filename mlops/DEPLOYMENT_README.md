# MLOps Deployment Guide

## Quick Deploy to RTX 8000 GPU Server

The `push` command syncs the WebQL MLOps pipeline to the RTX 8000 GPU training server with progress tracking.

### Basic Usage

```bash
# Use default settings (RTX 8000: 192.168.0.104)
make push

# Custom server
make push server=192.168.1.100

# Custom user  
make push user=myuser

# Custom folder
make push folder=~/my-training-dir

# All custom parameters
make push server=192.168.1.100 user=myuser folder=~/custom-path
```

### Default Configuration (RTX 8000)

```bash
REMOTE_SERVER := 192.168.0.104  # RTX 8000 GPU server
REMOTE_USER := yprift01  
REMOTE_DIR := ~/Dev/dr-web-training
```

### What Gets Synced

**Included:**
- ✅ All source code (`src/`)
- ✅ Configuration files (`configs/`)
- ✅ Training data (`data/`)
- ✅ Scripts and utilities (`scripts/`)
- ✅ Makefile and requirements

**Excluded:**
- ❌ Virtual environments (`.venv`)
- ❌ Python cache (`__pycache__`, `*.pyc`)
- ❌ Training outputs (`outputs/`)
- ❌ Model artifacts (`artifacts/`)
- ❌ Tokenized data cache (`data/tokenized/`)
- ❌ Git repository (`.git`)
- ❌ System files (`.DS_Store`)

### Rsync Options Used

- `--progress`: Shows file transfer progress
- `--update`: Only transfers newer files (preserves remote changes)
- `--archive`: Preserves permissions, timestamps, symbolic links
- `--verbose`: Shows which files are being transferred
- `--compress`: Compresses data during transfer

### Complete Deployment Workflow

```bash
# 1. Sync MLOps to RTX 8000 server
make push

# 2. SSH to RTX 8000 server  
ssh yprift01@192.168.0.104

# 3. Setup environment on remote
cd ~/Dev/dr-web-training
make venv && source .venv/bin/activate
make install

# 4. Start training
make train TRAIN_CONFIG=train_webql

# 5. Evaluate results
make eval EVAL_CONFIG=eval_webql
make eval EVAL_CONFIG=eval_webql_baseline
```

### Custom Server Examples

```bash
# Deploy to different GPU server
make push server=gpu-server.local user=researcher

# Deploy to cloud instance
make push server=my-gpu-instance.cloud.com folder=/opt/training

# Deploy with all parameters
make push \
  server=192.168.1.50 \
  user=ml-engineer \
  folder=~/projects/webql-training
```

### Troubleshooting

**Permission Denied:**
```bash
# Ensure SSH key access is configured
ssh-copy-id user@server
```

**Directory Doesn't Exist:**
```bash
# Create target directory on remote server
ssh user@server "mkdir -p ~/Dev/dr-web-training"
```

**Large File Transfer:**
- Training data (~345 examples) transfers quickly
- Conversion only happens once (cached locally)
- Subsequent syncs only transfer changed files

### Next Steps After Sync

The command automatically displays next steps:
```bash
✅ MLOps sync complete to user@server:folder
📋 Next steps on remote server:
   ssh user@server  
   cd folder
   make venv && source .venv/bin/activate
   make install
   make train TRAIN_CONFIG=train_webql
```