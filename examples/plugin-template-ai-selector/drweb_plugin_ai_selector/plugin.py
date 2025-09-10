"""
AI-Selector Plugin for DR Web Engine
"""

from typing import List, Dict, Any, Optional

# Import interfaces from dr-web-engine
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor

from .processor import AISelectorProcessor
from .config import AIConfig


class AISelectorPlugin(DrWebPlugin):
    """
    AI-Selector plugin that provides natural language element selection.
    
    This plugin allows users to describe elements in plain English instead
    of writing complex XPath or CSS selectors.
    """
    
    def __init__(self):
        self._config = None
        self._processor = None
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="drweb-plugin-ai-selector",
            version="1.0.0",
            description="AI-powered element selector that converts natural language descriptions to XPath selectors",
            author="DR Web Engine Team",
            homepage="https://github.com/starlitlog/drweb-plugin-ai-selector",
            supported_step_types=["AiSelectStep"],
            dependencies=["requests", "pydantic"],
            min_drweb_version="0.10.0",
            enabled=True
        )
    
    def get_processors(self) -> List[StepProcessor]:
        """Return list of step processors provided by this plugin."""
        if not self._processor:
            self._processor = AISelectorProcessor(self._config)
        return [self._processor]
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        # Create AI config from provided configuration
        ai_config = AIConfig()
        
        # Override defaults with provided config
        if "endpoint" in config:
            ai_config.endpoint = config["endpoint"]
        if "api_key" in config:
            ai_config.api_key = config["api_key"]
        if "model" in config:
            ai_config.model = config["model"]
        if "temperature" in config:
            ai_config.temperature = float(config["temperature"])
        if "max_tokens" in config:
            ai_config.max_tokens = int(config["max_tokens"])
        if "timeout" in config:
            ai_config.timeout = int(config["timeout"])
        
        self._config = ai_config
        
        # Reinitialize processor if it exists
        if self._processor:
            self._processor = AISelectorProcessor(self._config)
    
    def finalize(self) -> None:
        """Cleanup plugin resources."""
        if self._processor:
            # Clear cache to free memory
            self._processor.cache.clear()
        self._processor = None
        self._config = None
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Return JSON schema for plugin configuration."""
        return {
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "AI API endpoint URL",
                    "default": "https://api.openai.com/v1/chat/completions",
                    "examples": [
                        "https://api.openai.com/v1/chat/completions",
                        "http://localhost:11434/api/chat",
                        "https://api.together.xyz/v1/chat/completions"
                    ]
                },
                "api_key": {
                    "type": ["string", "null"],
                    "description": "API key for the AI service (optional for local services)",
                    "default": None
                },
                "model": {
                    "type": "string", 
                    "description": "AI model to use",
                    "default": "gpt-4o-mini",
                    "examples": [
                        "gpt-4o-mini",
                        "gpt-4o",
                        "llama3.2:3b",
                        "codellama:7b"
                    ]
                },
                "temperature": {
                    "type": "number",
                    "description": "AI temperature for response randomness",
                    "default": 0.3,
                    "minimum": 0.0,
                    "maximum": 2.0
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens in AI response",
                    "default": 500,
                    "minimum": 50,
                    "maximum": 2000
                },
                "timeout": {
                    "type": "integer",
                    "description": "API request timeout in seconds",
                    "default": 30,
                    "minimum": 5,
                    "maximum": 300
                }
            },
            "additionalProperties": False
        }