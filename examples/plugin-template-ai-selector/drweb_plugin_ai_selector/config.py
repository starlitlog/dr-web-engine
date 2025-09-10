"""
Configuration for AI-Selector Plugin
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIConfig:
    """AI API configuration."""
    endpoint: str = os.getenv("AI_SELECTOR_ENDPOINT", "https://api.openai.com/v1/chat/completions")
    api_key: Optional[str] = os.getenv("AI_SELECTOR_API_KEY")
    model: str = os.getenv("AI_SELECTOR_MODEL", "gpt-4o-mini")
    temperature: float = 0.3
    max_tokens: int = 500
    timeout: int = 30


def configure_ai_selector(
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> AIConfig:
    """
    Configure AI selector with custom settings.
    
    Examples:
        # OpenAI
        config = configure_ai_selector(
            endpoint="https://api.openai.com/v1/chat/completions",
            api_key="sk-...",
            model="gpt-4o-mini"
        )
        
        # Local Ollama
        config = configure_ai_selector(
            endpoint="http://localhost:11434/api/chat",
            model="llama3.2:3b"
        )
        
        # Custom OpenAI-compatible endpoint
        config = configure_ai_selector(
            endpoint="https://my-ai-service.com/v1/chat/completions",
            api_key="my-key",
            model="custom-model"
        )
    """
    config = AIConfig()
    
    if endpoint:
        config.endpoint = endpoint
    if api_key:
        config.api_key = api_key
    if model:
        config.model = model
    
    return config