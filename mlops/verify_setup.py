#!/usr/bin/env python3
"""
Verify WebQL MLOps setup is ready for training
"""

import json
import glob
from pathlib import Path

def verify_data():
    """Verify training and evaluation data"""
    print("🔍 Verifying data setup...")
    
    # Check training data
    train_files = glob.glob("data/converted_webql_*.jsonl")
    print(f"✅ Found {len(train_files)} training files")
    
    total_examples = 0
    for file_path in train_files:
        with open(file_path, 'r') as f:
            examples = len(f.readlines())
            total_examples += examples
            print(f"   - {Path(file_path).name}: {examples} examples")
    
    print(f"✅ Total training examples: {total_examples}")
    
    # Check evaluation data
    eval_files = ["data/eval/test.jsonl", "data/eval/dev.jsonl", "data/eval/adversarial.jsonl"]
    for eval_file in eval_files:
        if Path(eval_file).exists():
            with open(eval_file, 'r') as f:
                examples = len(f.readlines())
                print(f"✅ {eval_file}: {examples} examples")
        else:
            print(f"❌ Missing: {eval_file}")
    
    # Verify data format
    print("\n🔍 Verifying data format...")
    sample_file = train_files[0] if train_files else None
    if sample_file:
        with open(sample_file, 'r') as f:
            first_line = f.readline().strip()
            try:
                data = json.loads(first_line)
                if "prompt" in data and "completion" in data:
                    print("✅ Data format: prompt/completion ✓")
                    print(f"   Sample prompt: {data['prompt'][:80]}...")
                else:
                    print("❌ Data format: Missing prompt/completion fields")
            except json.JSONDecodeError:
                print("❌ Data format: Invalid JSON")

def verify_configs():
    """Verify configuration files"""
    print("\n🔍 Verifying configurations...")
    
    configs = [
        "configs/train_webql.yaml",
        "configs/eval_webql.yaml", 
        "configs/eval_webql_baseline.yaml"
    ]
    
    for config_path in configs:
        if Path(config_path).exists():
            print(f"✅ {config_path}: Found")
            
            # Check key settings for training config by reading file
            if "train_webql" in config_path:
                with open(config_path, 'r') as f:
                    content = f.read()
                    if "codellama/CodeLlama-7b-Instruct-hf" in content:
                        print(f"   - Model: CodeLlama-7b-Instruct ✓")
                    if "converted_webql_*.jsonl" in content:
                        print(f"   - Dataset: converted_webql_*.jsonl ✓")
                    if "max_length: 1024" in content:
                        print(f"   - Max length: 1024 ✓")
        else:
            print(f"❌ Missing: {config_path}")

def verify_scripts():
    """Verify required scripts"""
    print("\n🔍 Verifying scripts...")
    
    scripts = [
        "scripts/convert_webql_format.py",
        "src/main.py",
        "Makefile"
    ]
    
    for script in scripts:
        if Path(script).exists():
            print(f"✅ {script}")
        else:
            print(f"❌ Missing: {script}")

def print_next_steps():
    """Print next steps for training"""
    print("\n🚀 Setup complete! Next steps:")
    print("\n📋 For local testing:")
    print("   1. make venv && source .venv/bin/activate")
    print("   2. make install")
    print("   3. python -m src.main list-configs")
    print("\n🖥️  For GPU training:")
    print("   1. Copy mlops/ directory to GPU machine")
    print("   2. make venv && source .venv/bin/activate")
    print("   3. make install") 
    print("   4. make train TRAIN_CONFIG=train_webql")
    print("   5. make eval EVAL_CONFIG=eval_webql")
    print("   6. make eval EVAL_CONFIG=eval_webql_baseline")
    print("\n📊 Expected training time: 2-4 hours on RTX 4090")
    print("💾 Expected model size: ~3GB (LoRA adapter)")

def main():
    print("🔧 WebQL MLOps Setup Verification\n")
    
    verify_data()
    verify_configs()
    verify_scripts()
    print_next_steps()

if __name__ == "__main__":
    main()