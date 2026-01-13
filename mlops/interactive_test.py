#!/usr/bin/env python3
"""
Interactive WebQL model testing
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Fix HF_HOME for large disk
os.environ["HF_HOME"] = "/mnt/diskA/.cache/huggingface"

def load_model():
    """Load the trained model"""
    print("🔄 Loading trained model...")
    
    base_model_name = "meta-llama/Llama-3.2-1B-Instruct"
    model_path = "outputs/runs/latest/model"
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Load fine-tuned adapter
    model = PeftModel.from_pretrained(base_model, model_path)
    model.eval()
    
    return model, tokenizer

def generate_webql(model, tokenizer, prompt):
    """Generate WebQL from prompt"""
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=300,
            do_sample=True,
            temperature=0.1,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    # Decode only generated part
    generated = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return generated

def main():
    try:
        model, tokenizer = load_model()
        print("✅ Model loaded successfully!")
        print("\n" + "="*50)
        print("INTERACTIVE WEBQL TESTING")
        print("="*50)
        print("Type your requests (or 'quit' to exit)")
        print()
        
        while True:
            # Get user input
            user_input = input("\n🤔 What do you want to scrape? ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # Format as training prompt
            prompt = f"Write a WebQL query to extract data from a website\n\nInput: {user_input}\n\nGenerate a WebQL query:"
            
            print(f"\n📝 Prompt: {prompt}")
            print("\n🤖 Generated WebQL:")
            print("-" * 30)
            
            # Generate
            generated = generate_webql(model, tokenizer, prompt)
            print(generated)
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the model is trained and accessible!")

if __name__ == "__main__":
    main()