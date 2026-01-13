from pathlib import Path
from typing import List, Optional
import glob
import json

from datasets import load_dataset, Dataset


def _resolve_data_files(path: str, pattern: Optional[str]) -> List[str]:
    """Return a sorted list of JSONL files based on file/dir/pattern input."""
    p = Path(path)
    files: List[Path] = []

    if p.is_file():
        files = [p]
    elif p.is_dir():
        glob_pattern = pattern or "*.jsonl"
        files = sorted(p.glob(glob_pattern))
    else:
        # Treat the provided path as a glob string (e.g., ./data/*.jsonl)
        files = [Path(match) for match in sorted(glob.glob(path))]

    if not files:
        where = f"{path} (pattern={pattern})"
        raise FileNotFoundError(f"No JSONL files matched {where}")

    return [str(f) for f in files]


def _format_messages(messages: List) -> str:
    """Convert chat messages to training text.

    Handles both formats:
    - Direct: [{"role": "user", "content": "..."}, ...]
    - Nested: [[{"role": "user", "content": "..."}, ...]]
    """
    # Handle nested structure (list of conversations)
    if messages and isinstance(messages[0], list):
        messages = messages[0]  # Unwrap the outer list

    parts = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            elif role == "system":
                parts.append(f"System: {content}")
    return "\n".join(parts)


def load_jsonl_dataset(path: str, pattern: Optional[str] = None, data_format: str = "prompt_completion"):
    """Loads one or many JSONL files as a Hugging Face Dataset.

    Args:
        path: Path to file or directory
        pattern: Glob pattern for files
        data_format: "messages" for chat format, "prompt_completion" for prompt/completion format
    """
    data_files = _resolve_data_files(path, pattern)

    if data_format == "messages":
        # Load messages format manually and convert to text
        records = []
        for file_path in data_files:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        obj = json.loads(line)
                        if "messages" in obj:
                            text = _format_messages(obj["messages"])
                            records.append({"text": text})
        return Dataset.from_list(records)
    else:
        # Original prompt/completion format
        dataset = load_dataset("json", data_files=data_files)
        return dataset["train"]
