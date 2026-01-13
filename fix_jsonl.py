#!/usr/bin/env python3
"""
Fix JSONL files with concatenated JSON objects
"""
import json
import re
import os
from pathlib import Path

def fix_jsonl_file(filepath):
    print(f"Fixing {filepath}...")
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split on }{ pattern to separate concatenated JSON objects
    # This regex finds }{ with possible whitespace in between
    parts = re.split(r'\}\s*\{', content)
    
    fixed_lines = []
    
    for i, part in enumerate(parts):
        # Add back the braces that were removed by split
        if i == 0:
            # First part already has opening brace
            if not part.strip().endswith('}'):
                part += '}'
        elif i == len(parts) - 1:
            # Last part already has closing brace
            if not part.strip().startswith('{'):
                part = '{' + part
        else:
            # Middle parts need both braces
            part = '{' + part + '}'
        
        # Clean up common issues
        part = part.strip()
        if not part:
            continue
            
        # Fix common quote issues
        part = re.sub(r'(?<!\\)"(?![\s,\]\}])', '\\"', part)
        
        # Try to parse as JSON to validate
        try:
            json_obj = json.loads(part)
            fixed_lines.append(json.dumps(json_obj, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON in {filepath}: {part[:100]}...")
            print(f"Error: {e}")
            
            # Try to fix common issues and retry
            try:
                # Fix unescaped quotes in output field
                if '"output":' in part:
                    # Find the output field and properly escape it
                    match = re.search(r'"output":\s*"([^"]+(?:\\"[^"]*)*)"', part, re.DOTALL)
                    if match:
                        output_content = match.group(1)
                        # Properly escape the content
                        escaped_content = output_content.replace('"', '\\"').replace('\n', '\\n')
                        part = part.replace(match.group(0), f'"output": "{escaped_content}"')
                        
                json_obj = json.loads(part)
                fixed_lines.append(json.dumps(json_obj, ensure_ascii=False))
                print(f"  ✓ Fixed after escaping")
            except:
                print(f"  ✗ Could not fix, skipping")
                continue
    
    # Write the fixed file
    backup_path = str(filepath) + '.backup'
    if os.path.exists(filepath):
        os.rename(filepath, backup_path)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in fixed_lines:
            f.write(line + '\n')
    
    print(f"Fixed {filepath}: {len(fixed_lines)} valid JSON objects")
    return len(fixed_lines)

def main():
    # Fix all JSONL files in the data directory
    data_dir = Path('./data')
    total_fixed = 0
    
    if not data_dir.exists():
        print("No data directory found")
        return
    
    for filepath in data_dir.glob('*.jsonl'):
        count = fix_jsonl_file(filepath)
        total_fixed += count
    
    print(f"\nTotal fixed JSON objects: {total_fixed}")

if __name__ == "__main__":
    main()