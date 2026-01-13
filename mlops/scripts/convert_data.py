#!/usr/bin/env python3
"""Convert ChatGPT messages format to universal prompt/completion JSONL.

Converts from:
- Multi-line ChatGPT export (messages format)
- Single-line messages format

To:
- Universal prompt/completion format (works with all models)
"""

import json
import re
import sys
from pathlib import Path


def messages_to_prompt_completion(messages):
    """Convert messages array to prompt/completion format.

    Takes first user message as prompt, last assistant message as completion.
    Handles nested list structure [[{...}]] or flat [{...}]
    """
    # Handle nested structure
    if messages and isinstance(messages[0], list):
        messages = messages[0]

    user_messages = [m['content'] for m in messages if isinstance(m, dict) and m.get('role') == 'user']
    assistant_messages = [m['content'] for m in messages if isinstance(m, dict) and m.get('role') == 'assistant']

    if not user_messages or not assistant_messages:
        return None

    # Use first user message as prompt, last assistant as completion
    return {
        "prompt": user_messages[0],
        "completion": assistant_messages[-1]
    }


def is_prompt_completion_format(obj):
    """Check if object is already in prompt/completion format."""
    return ("prompt" in obj and "completion" in obj) or \
           ("instruction" in obj and "output" in obj)


def convert_file(file_path: Path) -> int:
    """Convert a file to prompt/completion format.

    Returns number of records converted.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Try to load as single JSON first (multi-line export)
    try:
        data = json.loads(content)
        if isinstance(data, list):
            # Array of message objects
            records = []
            for item in data:
                if "messages" in item:
                    converted = messages_to_prompt_completion(item["messages"])
                    if converted:
                        records.append(converted)
                elif is_prompt_completion_format(item):
                    records.append(item)
        elif isinstance(data, dict) and "messages" in data:
            # Single message object
            converted = messages_to_prompt_completion(data["messages"])
            records = [converted] if converted else []
        else:
            records = []
    except json.JSONDecodeError:
        # Not valid single JSON, try JSONL (line by line)
        records = []
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle multi-line blocks separated by empty lines
            if not line.startswith('{'):
                continue

            # Try to find complete JSON object
            block = line
            try:
                obj = json.loads(block)
            except json.JSONDecodeError:
                # Multi-line, accumulate
                continue

            if "messages" in obj:
                converted = messages_to_prompt_completion(obj["messages"])
                if converted:
                    records.append(converted)
            elif is_prompt_completion_format(obj):
                records.append(obj)

    if records:
        # Write back as JSONL
        with open(file_path, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')

    return len(records)


def main():
    data_dir = Path("./data")

    if not data_dir.exists():
        print(f"Error: Data directory {data_dir} not found")
        sys.exit(1)

    jsonl_files = list(data_dir.glob("*.jsonl"))

    if not jsonl_files:
        print(f"No .jsonl files found in {data_dir}")
        sys.exit(0)

    print(f"Found {len(jsonl_files)} JSONL files in {data_dir}\n")

    converted = 0
    skipped = 0

    for file_path in sorted(jsonl_files):
        # Quick check if already in prompt/completion format
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            if first_line:
                try:
                    obj = json.loads(first_line)
                    if is_prompt_completion_format(obj):
                        print(f"✓ {file_path.name} - already prompt/completion, skipping")
                        skipped += 1
                        continue
                except json.JSONDecodeError:
                    pass

        count = convert_file(file_path)
        if count > 0:
            print(f"✓ {file_path.name} - converted {count} records")
            converted += 1
        else:
            print(f"⚠ {file_path.name} - no records converted")

    print(f"\nDone! Converted: {converted}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
