#!/usr/bin/env python3
"""
Improved chat script for testing LoRA fine-tuned models.
Fixes CUDA probability tensor errors with better error handling and generation parameters.

Usage:
    python chat.py <base_model> <lora_adapter_path>
    
Example:
    python chat.py google/gemma-3-4b-it ./results/checkpoint-500
"""

import argparse
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    GenerationConfig,
    BitsAndBytesConfig
)
from peft import PeftModel
import warnings
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model_and_tokenizer(base_model_name, adapter_path=None):
    """Load base model and optionally apply LoRA adapter."""
    try:
        # Load tokenizer
        logger.info(f"Loading tokenizer from {base_model_name}")
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        
        # Add padding token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id

        # Configure quantization for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        # Load base model
        logger.info(f"Loading base model {base_model_name}")
        
        # Try flash attention first, fallback to regular attention
        try:
            model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                trust_remote_code=True,
                attn_implementation="flash_attention_2"
            )
        except Exception as e:
            logger.warning(f"Flash attention failed, using regular attention: {e}")
            model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                trust_remote_code=True
            )

        # Load LoRA adapter if provided
        if adapter_path:
            logger.info(f"Loading LoRA adapter from {adapter_path}")
            try:
                model = PeftModel.from_pretrained(model, adapter_path)
                logger.info("Merging LoRA weights...")
                model = model.merge_and_unload()  # Merge adapter weights for stable inference
            except Exception as e:
                logger.error(f"Failed to load LoRA adapter: {e}")
                logger.info("Continuing with base model only...")
                pass
            
        model.eval()  # Set to evaluation mode
        return model, tokenizer
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def generate_response(model, tokenizer, prompt, max_length=512, temperature=0.7):
    """Generate response with robust error handling."""
    try:
        # Prepare input
        inputs = tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        if torch.cuda.is_available():
            inputs = inputs.cuda()

        # Generation config with safe parameters
        generation_config = GenerationConfig(
            max_new_tokens=max_length,
            temperature=max(temperature, 0.1),  # Ensure temperature is not too low
            do_sample=True,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
            return_dict_in_generate=True,
            output_scores=False  # Disable score computation to avoid probability issues
        )

        # Generate with error handling
        with torch.no_grad():
            try:
                outputs = model.generate(
                    inputs,
                    generation_config=generation_config,
                    attention_mask=torch.ones_like(inputs)
                )
                
                # Extract generated tokens (excluding input)
                generated_tokens = outputs.sequences[0][inputs.shape[1]:]
                response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
                
                return response.strip()
                
            except RuntimeError as e:
                if "probability tensor contains either `inf`, `nan` or element < 0" in str(e):
                    logger.warning("Probability tensor error detected. Retrying with greedy decoding...")
                    # Fallback to greedy decoding
                    generation_config.do_sample = False
                    generation_config.temperature = None
                    generation_config.top_p = None
                    generation_config.top_k = None
                    
                    outputs = model.generate(
                        inputs,
                        generation_config=generation_config,
                        attention_mask=torch.ones_like(inputs)
                    )
                    
                    generated_tokens = outputs.sequences[0][inputs.shape[1]:]
                    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
                    return response.strip()
                else:
                    raise e
                    
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        return f"Error generating response: {e}"

def chat_loop(model, tokenizer):
    """Interactive chat loop."""
    print("\n🤖 LoRA Model Chat Interface")
    print("Type 'quit', 'exit', or 'q' to end the conversation")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            print("\n🤖 Assistant: ", end="", flush=True)
            
            # Format prompt (adjust based on your model's chat template)
            if hasattr(tokenizer, 'apply_chat_template'):
                messages = [{"role": "user", "content": user_input}]
                prompt = tokenizer.apply_chat_template(messages, tokenize=False)
            else:
                # Fallback formatting for models without chat template
                prompt = f"<start_of_turn>user\n{user_input}<end_of_turn>\n<start_of_turn>model\n"
            
            response = generate_response(model, tokenizer, prompt)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            print(f"\n❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Chat with a LoRA fine-tuned model")
    parser.add_argument("base_model", help="Base model name or path")
    parser.add_argument("adapter_path", nargs="?", help="Path to LoRA adapter (optional)")
    parser.add_argument("--max-length", type=int, default=512, help="Maximum response length")
    parser.add_argument("--temperature", type=float, default=0.7, help="Generation temperature")
    
    args = parser.parse_args()
    
    try:
        # Load model and tokenizer
        model, tokenizer = load_model_and_tokenizer(args.base_model, args.adapter_path)
        
        # Print model info
        print(f"\n✅ Successfully loaded:")
        print(f"   Base model: {args.base_model}")
        if args.adapter_path:
            print(f"   LoRA adapter: {args.adapter_path}")
        print(f"   Device: {next(model.parameters()).device}")
        print(f"   Model dtype: {next(model.parameters()).dtype}")
        
        # Start chat
        chat_loop(model, tokenizer)
        
    except Exception as e:
        logger.error(f"Failed to initialize chat: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()