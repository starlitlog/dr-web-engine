#!/usr/bin/env python3
"""
Quick test script for trained WebQL model
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
from pathlib import Path
import warnings

# Fix environment variable deprecation warning (must be set before importing transformers)
# Use large disk for cache to avoid filling system disk
os.environ["HF_HOME"] = "/mnt/diskA/.cache/huggingface"
if "TRANSFORMERS_CACHE" in os.environ:
    del os.environ["TRANSFORMERS_CACHE"]

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

def load_trained_model(model_path="outputs/runs/latest/model"):
    """Load the trained model and tokenizer"""
    print(f"Loading model from: {model_path}")
    
    # Load base model and tokenizer  
    base_model_name = "meta-llama/Llama-3.2-1B-Instruct"  # From incremental config
    
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Load LoRA adapter
    model = PeftModel.from_pretrained(base_model, model_path)
    model.eval()
    
    return model, tokenizer

def generate_webql(model, tokenizer, prompt, max_length=256):
    """Generate WebQL from a prompt"""
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    
    # Move inputs to same device as model
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_length,
            do_sample=True,
            temperature=0.1,  # Low temperature for consistent output
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    # Decode only the generated part
    generated_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return generated_text

def test_webql_generation():
    """Test the model with sample prompts"""
    
    # Check if model exists
    model_path = "outputs/runs/latest/model"
    if not Path(model_path).exists():
        print(f"❌ No trained model found at {model_path}")
        print("Run training first: make train TRAIN_CONFIG=train_webql_tiny")
        return
    
    try:
        print("🔄 Loading trained model...")
        model, tokenizer = load_trained_model(model_path)
        print("✅ Model loaded successfully!")
        
        # Test prompts (similar to training data format)
        test_prompts = [
            "Write a basic WebQL query to extract quotes from quotes.toscrape.com\n\nInput: I want to extract quotes, authors, and tags from the quotes website\n\nGenerate a WebQL query:",
            
            "Create a WebQL query for extracting Hacker News articles\n\nInput: Extract titles, URLs, and ranks from Hacker News front page\n\nGenerate a WebQL query:",
            
            "Write a WebQL query to scrape product information\n\nInput: Extract product names and prices from an e-commerce site\n\nGenerate a WebQL query:"
        ]
        
        print("\n🧪 Testing WebQL generation...\n")
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"{'='*50}")
            print(f"TEST {i}")
            print(f"{'='*50}")
            print(f"Prompt: {prompt[:80]}...")
            print("\nGenerated WebQL:")
            print("-" * 30)
            
            try:
                generated = generate_webql(model, tokenizer, prompt)
                print(generated)
                
                # Try to parse as JSON to check syntax
                try:
                    if generated.strip().startswith('{') and generated.strip().endswith('}'):
                        parsed = json.loads(generated.strip())
                        print("\n✅ Valid JSON syntax!")
                        
                        # Check for WebQL structure
                        if "@url" in parsed and "@steps" in parsed:
                            print("✅ Contains WebQL structure (@url, @steps)")
                        else:
                            print("⚠️  Missing WebQL structure (@url, @steps)")
                    else:
                        print("⚠️  Output doesn't look like JSON")
                        
                except json.JSONDecodeError:
                    print("❌ Invalid JSON syntax")
                    
            except Exception as e:
                print(f"❌ Generation error: {e}")
            
            print("\n")
        
        print("🎯 Testing complete!")
        print("\nNext steps:")
        print("✅ If outputs look good → Try train_webql_incremental (45 mins)")
        print("❌ If outputs are poor → Check training data or try different approach")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("Make sure you've run: make train TRAIN_CONFIG=train_webql_tiny")

if __name__ == "__main__":
    test_webql_generation()