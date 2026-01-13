# === AnySecret-LLM Makefile ===
# Quick commands for training, evaluation, and publishing

# Default Python interpreter
PYTHON := python3
MODULE := src.main

# Config name (Hydra base)
TRAIN_CONFIG := train
EVAL_CONFIG := eval
BASELINE_EVAL_CONFIG := eval_baseline

# Virtual environment (optional)
VENV := .venv

# === WebQL MLOps Remote Training (RTX 8000) ===
REMOTE_SERVER := 192.168.0.104
REMOTE_USER := yprift01
REMOTE_DIR := ~/Dev/dr-web-training

# === LakeFS Metadata Management ===
R2_ENDPOINT := https://b34c59f008d4bdd78b7d2eb223cee7c2.r2.cloudflarestorage.com
LAKEFS_BUCKET := mlops-lakefs
DOCKER_COMPOSE_PATH := infra/docker-compose

.PHONY: push ssh-train ssh-eval ssh-init push-metadata pull-metadata

# --- Sync WebQL MLOps to remote GPU server ---
push:
	$(eval SERVER := $(if $(server),$(server),$(REMOTE_SERVER)))
	$(eval USER := $(if $(user),$(user),$(REMOTE_USER)))  
	$(eval FOLDER := $(if $(folder),$(folder),$(REMOTE_DIR)))
	@echo "🚀 Syncing WebQL MLOps to GPU server (RTX 8000)..."
	@echo "   Target: $(USER)@$(SERVER):$(FOLDER)"
	@echo "   Source: $(shell pwd)"
	@echo ""
	rsync -avz --progress --update \
		--exclude '.venv' \
		--exclude '__pycache__' \
		--exclude '*.pyc' \
		--exclude '.DS_Store' \
		--exclude 'outputs/' \
		--exclude 'artifacts/' \
		--exclude '.git' \
		--exclude 'data/tokenized/' \
		. $(USER)@$(SERVER):$(FOLDER)
	@echo ""
	@echo "✅ WebQL MLOps sync complete to $(USER)@$(SERVER):$(FOLDER)"
	@echo "📋 Next steps on RTX 8000 server:"
	@echo "   ssh $(USER)@$(SERVER)"
	@echo "   cd $(FOLDER)"
	@echo "   make venv && source .venv/bin/activate"
	@echo "   make install"
	@echo "   make train TRAIN_CONFIG=train_webql"


# --- Initialize remote environment once ---
ssh-init:
	@echo "🧰 Initializing remote environment..."
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) "\
		cd $(REMOTE_DIR) && \
		python3 -m venv .venv && \
		source .venv/bin/activate && \
		make install \
	"
	@echo "✅ Remote environment ready."

# --- Run full training remotely (always safe) ---
ssh-train:
	@echo "💻 Starting remote training..."
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) "\
		cd $(REMOTE_DIR) && \
		source .venv/bin/activate && \
		PYTHONPATH=. python3 -m src.main train --config-name $(TRAIN_CONFIG) \
	"

# --- Run training in background with tmux (survives disconnect) ---
ssh-train-bg:
	@echo "💻 Starting remote training in tmux session 'train'..."
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) "\
		tmux kill-session -t train 2>/dev/null || true && \
		tmux new-session -d -s train '\
			cd $(REMOTE_DIR) && \
			source .venv/bin/activate && \
			PYTHONPATH=. python3 -m src.main train --config-name $(TRAIN_CONFIG); \
			echo \"Training complete. Press enter to exit.\"; \
			read \
		' \
	"
	@echo "✅ Training started in background. Reconnect with: ssh $(REMOTE_USER)@$(REMOTE_SERVER) -t 'tmux attach -t train'"

# Ensure venv/bin is in path if it exists
ifneq ("$(wildcard $(VENV)/bin/activate)","")
    ACTIVATE := . $(VENV)/bin/activate &&
else
    ACTIVATE :=
endif

# === Core commands ===

.PHONY: help venv install clean train eval publish format lint convert tokenize merge gguf setup-cache

help:
	@echo "Available targets:"
	@echo "  make venv          - Create a virtual environment (.venv)"
	@echo "  make install       - Install dependencies"
	@echo "  make setup-cache   - Setup HuggingFace cache on large disk (/mnt/diskA)"
	@echo "  make convert       - Convert ChatGPT format to JSONL"
	@echo "  make tokenize      - Pre-tokenize dataset (speeds up training)"
	@echo "  make train         - Run training pipeline"
	@echo "  make eval          - Run evaluation pipeline"
	@echo "  make merge         - Merge LoRA adapter into base model"
	@echo "  make gguf          - Convert to GGUF (use QUANT=Q4_K_M to override)"
	@echo "  make publish       - Copy model to local artifacts"
	@echo "  make publish-hf    - Push model to HuggingFace Hub"
	@echo "  make clean         - Remove generated outputs"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Run lint checks"
	@echo "  make push          - Sync to remote GPU server (server=IP user=USER folder=PATH)"
	@echo ""
	@echo "Environment:"
	@echo "  Create .env file with HF_HOME, CUDA_VISIBLE_DEVICES, etc. (see .env template)"
	@echo "  make push-metadata - Backup LakeFS metadata to R2"
	@echo "  make pull-metadata - Restore LakeFS metadata from R2"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Activate with: source $(VENV)/bin/activate"

install:
	$(ACTIVATE) pip install -r requirements.txt || pip install typer hydra-core omegaconf

setup-cache:
	@echo "🗂️  Setting up HuggingFace cache on large disk..."
	./setup_cache.sh

convert:
	@echo "🔄 Converting ChatGPT format files to JSONL..."
	$(ACTIVATE) $(PYTHON) scripts/convert_data.py
	@echo "✅ Conversion complete."

tokenize:
	@echo "🔤 Pre-tokenizing dataset (uses all CPU cores)..."
	$(ACTIVATE) $(PYTHON) scripts/tokenize_dataset.py -c configs/$(TRAIN_CONFIG).yaml
	@echo "✅ Tokenized dataset saved to data/tokenized"
	@echo "⚠️  Update your config: dataset_path: data/tokenized"

train:
	$(ACTIVATE) bash -c 'set -a; test -f .env && source .env; PYTHONPATH=./ $(PYTHON) -m $(MODULE) train --config-name $(TRAIN_CONFIG)'

eval:
	$(ACTIVATE) bash -c 'set -a; test -f .env && source .env; $(PYTHON) -m $(MODULE) eval --config-name $(EVAL_CONFIG)'

eval-baseline:
	$(ACTIVATE) bash -c 'set -a; test -f .env && source .env; $(PYTHON) -m $(MODULE) eval --config-name $(BASELINE_EVAL_CONFIG)'

# === Model Packaging ===
QUANT := Q5_K_M
LLAMA_CPP := ../llama.cpp
CUDA_DEVICE := 0

merge:
	@echo "🔀 Merging LoRA adapter into base model..."
	$(ACTIVATE) $(PYTHON) scripts/merge_model.py outputs/runs/latest/model --cuda $(CUDA_DEVICE)
	@echo "✅ Merged model saved to outputs/runs/latest/merged"

gguf: merge
	@echo "📦 Converting to GGUF ($(QUANT))..."
	$(ACTIVATE) $(PYTHON) $(LLAMA_CPP)/convert_hf_to_gguf.py \
		outputs/runs/latest/merged \
		--outfile outputs/runs/latest/merged/model-f16.gguf \
		--outtype f16
	$(LLAMA_CPP)/build/bin/llama-quantize \
		outputs/runs/latest/merged/model-f16.gguf \
		outputs/runs/latest/merged/model-$(QUANT).gguf \
		$(QUANT)
	@echo "✅ GGUF model saved to outputs/runs/latest/merged/model-$(QUANT).gguf"

publish:
	$(ACTIVATE) $(PYTHON) -m $(MODULE) publish outputs/runs/latest/model

publish-hf:
	@echo "📤 Publishing to HuggingFace..."
	@test -f .env && export $$(grep -v '^#' .env | xargs) || true; \
	$(ACTIVATE) $(PYTHON) -m $(MODULE) publish-hf outputs/runs/latest/model
	@echo "✅ Published to HuggingFace"

clean:
	rm -rf outputs/__pycache__ */__pycache__ *.pyc
	@echo "Cleaned outputs and caches."

format:
	$(ACTIVATE) black src

lint:
	$(ACTIVATE) pylint src || echo "Lint issues (non-fatal)"
# --- Run evaluation remotely ---
ssh-eval:
	@echo "🧪 Starting remote evaluation..."
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) "\
		cd $(REMOTE_DIR) && \
		source .venv/bin/activate && \
		PYTHONPATH=. python3 -m src.main eval --config-name $(EVAL_CONFIG) \
	"

.PHONY: ssh-eval-baseline
ssh-eval-baseline:
	@echo "🧪 Starting remote baseline evaluation..."
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) "\
		cd $(REMOTE_DIR) && \
		source .venv/bin/activate && \
		PYTHONPATH=. python3 -m src.main eval --config-name $(BASELINE_EVAL_CONFIG) \
	"

# === LakeFS Metadata Management ===

push-metadata:
	@echo "🗄️  Backing up LakeFS metadata to R2..."
	docker compose -f $(DOCKER_COMPOSE_PATH)/docker-compose.yml --env-file $(DOCKER_COMPOSE_PATH)/base.env --env-file $(DOCKER_COMPOSE_PATH)/.env exec postgres pg_dump -U lakefs lakefs > postgres_backup.sql
	bash -c "set -a; source $(DOCKER_COMPOSE_PATH)/.env; aws s3 cp postgres_backup.sql s3://$(LAKEFS_BUCKET)/metadata/postgres_backup.sql --endpoint-url $(R2_ENDPOINT)"
	rm postgres_backup.sql
	@echo "✅ Metadata pushed to R2"

pull-metadata:
	@echo "⬇️  Restoring LakeFS metadata from R2..."
	bash -c "set -a; source $(DOCKER_COMPOSE_PATH)/.env; aws s3 cp s3://$(LAKEFS_BUCKET)/metadata/postgres_backup.sql postgres_backup.sql --endpoint-url $(R2_ENDPOINT)"
	docker compose -f $(DOCKER_COMPOSE_PATH)/docker-compose.yml --env-file $(DOCKER_COMPOSE_PATH)/base.env --env-file $(DOCKER_COMPOSE_PATH)/.env up -d postgres
	@echo "⏳ Waiting for Postgres to start..."
	@sleep 15
	docker compose -f $(DOCKER_COMPOSE_PATH)/docker-compose.yml --env-file $(DOCKER_COMPOSE_PATH)/base.env --env-file $(DOCKER_COMPOSE_PATH)/.env exec -T postgres psql -U lakefs lakefs < postgres_backup.sql
	rm postgres_backup.sql
	@echo "✅ Metadata restored from R2"
