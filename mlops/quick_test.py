#!/usr/bin/env python3
"""
Quick diagnostic test - check if model learned anything useful
"""

import os
import json

# Fix HF_HOME before importing transformers - use large disk
os.environ["HF_HOME"] = "/mnt/diskA/.cache/huggingface"
if "TRANSFORMERS_CACHE" in os.environ:
    del os.environ["TRANSFORMERS_CACHE"]

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def test_base_vs_finetuned():
    """Compare base model vs fine-tuned outputs"""
    
    print("🧪 Testing Base vs Fine-tuned Model")
    print("="*50)
    
    # Load base model
    print("📄 Loading base Llama-3.2-1B...")
    base_model_name = "meta-llama/Llama-3.2-1B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        dtype=torch.bfloat16,
        device_map="auto"
    )
    
    # Simple test prompt
    test_prompt = "Generate a JSON object with @url and @steps:"
    
    print(f"\nPrompt: {test_prompt}")
    print("\n🔶 BASE MODEL OUTPUT:")
    print("-" * 30)
    
    # Generate with base model
    inputs = tokenizer(test_prompt, return_tensors="pt")
    inputs = {k: v.to(base_model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = base_model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    base_output = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    print(base_output)
    
    # Test fine-tuned model if available
    model_path = "outputs/runs/latest/model"
    if os.path.exists(model_path):
        print(f"\n🔷 FINE-TUNED MODEL OUTPUT:")
        print("-" * 30)
        
        # Load fine-tuned model
        finetuned_model = PeftModel.from_pretrained(base_model, model_path)
        finetuned_model.eval()
        
        with torch.no_grad():
            outputs = finetuned_model.generate(
                input_ids=inputs["input_ids"], 
                attention_mask=inputs["attention_mask"],
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        finetuned_output = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        print(finetuned_output)
        
        print(f"\n📊 COMPARISON:")
        print(f"Base length: {len(base_output)}")
        print(f"Fine-tuned length: {len(finetuned_output)}")
        print(f"Contains '@url': {('@url' in finetuned_output)}")
        print(f"Contains '@steps': {('@steps' in finetuned_output)}")
        print(f"Looks like JSON: {finetuned_output.strip().startswith('{')}")
        
    else:
        print("❌ No fine-tuned model found")

def check_training_data():
    """Check if training data looks correct"""
    print(f"\n📁 TRAINING DATA CHECK:")
    print("=" * 30)
    
    data_files = [
        "data/converted_webql_basic_queries.jsonl"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"\n📄 {file_path}:")
            with open(file_path, 'r') as f:
                for i, line in enumerate(f.readlines()[:2]):  # First 2 examples
                    try:
                        data = json.loads(line.strip())
                        print(f"\nExample {i+1}:")
                        print(f"Prompt: {data['prompt'][:60]}...")
                        print(f"Completion: {data['completion'][:60]}...")
                        
                        # Check if completion contains WebQL structure
                        if '@url' in data['completion'] and '@steps' in data['completion']:
                            print("✅ Contains WebQL structure")
                        else:
                            print("❌ Missing WebQL structure")
                    except:
                        print(f"❌ Invalid JSON in line {i+1}")
        else:
            print(f"❌ File not found: {file_path}")

def main():
    check_training_data()
    test_base_vs_finetuned()
    
    print(f"\n🎯 DIAGNOSIS:")
    print("If fine-tuned model output is similar to base model:")
    print("  → Training was ineffective (try longer training)")
    print("If fine-tuned model contains WebQL elements:")
    print("  → Model learned something, but needs more training")
    print("If fine-tuned model generates SQL/REST:")
    print("  → Model confused, try different base model or approach")

if __name__ == "__main__":
    main()