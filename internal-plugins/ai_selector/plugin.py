"""
AI-Selector Plugin Implementation
"""

from typing import List, Dict, Any, Optional
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor
from engine.web_engine.plugins.ai_selector import AISelectorProcessor, AIConfig


class AISelectorPlugin(DrWebPlugin):
    """
    AI-Selector plugin that provides natural language element selection.
    
    This is an internal plugin shipped with DR Web Engine that allows users 
    to describe elements in plain English instead of writing complex XPath 
    or CSS selectors.
    """
    
    def __init__(self):
        self._config = None
        self._processor = None
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="ai-selector",
            version="1.0.0",
            description="AI-powered element selector for natural language queries",
            author="DR Web Engine Team",
            homepage="https://github.com/starlitlog/dr-web-engine",
            supported_step_types=["AiSelectStep"],
            dependencies=["requests"],
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