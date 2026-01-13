#!/bin/bash
# Setup HuggingFace cache on large disk

echo "🗂️  Setting up HuggingFace cache on large disk..."

# Create cache directory if it doesn't exist
CACHE_DIR="/mnt/diskA/.cache/huggingface"
mkdir -p "$CACHE_DIR"

# Set permissions
chmod 755 "$CACHE_DIR"

# Check if directory exists and is writable
if [ -w "$CACHE_DIR" ]; then
    echo "✅ Cache directory ready: $CACHE_DIR"
    echo "📊 Available space:"
    df -h "$CACHE_DIR"
else
    echo "❌ Cannot write to cache directory: $CACHE_DIR"
    echo "Run: sudo mkdir -p $CACHE_DIR && sudo chown $USER:$USER $CACHE_DIR"
    exit 1
fi

# Export environment variable for current session
export HF_HOME="$CACHE_DIR"

# Check if .env exists and update it
if [ -f .env ]; then
    echo "✅ .env file exists with HF_HOME=$CACHE_DIR"
else
    echo "❌ .env file not found - create it manually"
fi

echo "🎯 To permanently set for your user, add to ~/.bashrc:"
echo "export HF_HOME=/mnt/diskA/.cache/huggingface"