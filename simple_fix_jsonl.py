#!/usr/bin/env python3
"""
Simple fix for concatenated JSON objects in JSONL files
"""
import json
import re
import os
from pathlib import Path

def simple_fix_jsonl(filepath):
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split on }{ pattern - the main issue
    fixed_content = re.sub(r'\}\s*\{', '}\n{', content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    # Count lines for verification
    lines = fixed_content.strip().split('\n')
    valid_count = 0
    for line in lines:
        line = line.strip()
        if line:
            try:
                json.loads(line)
                valid_count += 1
            except:
                print(f"  Warning: Invalid JSON line: {line[:50]}...")
    
    print(f"  Fixed: {valid_count} valid JSON objects")
    return valid_count

def main():
    data_dir = Path('./data')
    if not data_dir.exists():
        print("No data directory found")
        return
    
    total = 0
    for filepath in data_dir.glob('*.jsonl'):
        if '.backup' not in str(filepath):
            count = simple_fix_jsonl(filepath)
            total += count
    
    print(f"\nTotal: {total} JSON objects")

if __name__ == "__main__":
    main()