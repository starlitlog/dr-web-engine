#!/usr/bin/env python3
"""
Convert WebQL training data from instruction format to prompt/completion format
for compatibility with the MLOps training pipeline.
"""

import json
import os
import glob
from pathlib import Path

def convert_instruction_to_prompt_completion(data):
    """Convert instruction format to prompt/completion format"""
    instruction = data.get("instruction", "")
    input_text = data.get("input", "")
    output_text = data.get("output", "")
    
    # Combine instruction and input into a prompt
    if input_text:
        prompt = f"{instruction}\n\nInput: {input_text}\n\nGenerate a WebQL query:"
    else:
        prompt = f"{instruction}\n\nGenerate a WebQL query:"
    
    return {
        "prompt": prompt,
        "completion": output_text
    }

def process_file(input_file, output_file):
    """Process a single JSONL file"""
    converted_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                converted_data = convert_instruction_to_prompt_completion(data)
                
                json.dump(converted_data, outfile, ensure_ascii=False)
                outfile.write('\n')
                converted_count += 1
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line in {input_file}: {e}")
                continue
    
    return converted_count

def main():
    data_dir = Path("data")
    
    # Process all webql_*.jsonl files
    pattern = str(data_dir / "webql_*.jsonl")
    files = glob.glob(pattern)
    
    total_converted = 0
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        output_path = data_dir / f"converted_{file_name}"
        
        print(f"Converting {file_name}...")
        converted_count = process_file(file_path, output_path)
        total_converted += converted_count
        
        print(f"  → {converted_count} examples converted to {output_path}")
    
    print(f"\nTotal: {total_converted} examples converted across {len(files)} files")
    print("\nConverted files are prefixed with 'converted_' and ready for training.")
    print("Update your config to use: dataset_pattern: 'converted_webql_*.jsonl'")

if __name__ == "__main__":
    main()