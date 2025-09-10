"""
JSON-LD Extractor Plugin Implementation
"""

from typing import List, Dict, Any
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor
from engine.web_engine.plugins.jsonld_extractor import JsonLdExtractorProcessor


class JsonLdExtractorPlugin(DrWebPlugin):
    """
    JSON-LD Extractor plugin for structured data extraction.
    
    This internal plugin extracts JSON-LD structured data from web pages,
    commonly used for schema.org markup, product information, articles, etc.
    """
    
    def __init__(self):
        self._processor = None
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="jsonld-extractor",
            version="1.0.0",
            description="Extracts JSON-LD structured data from web pages",
            author="DR Web Engine Team",
            homepage="https://github.com/starlitlog/dr-web-engine",
            supported_step_types=["JsonLdStep"],
            dependencies=[],
            min_drweb_version="0.10.0",
            enabled=True
        )
    
    def get_processors(self) -> List[StepProcessor]:
        """Return list of step processors provided by this plugin."""
        if not self._processor:
            self._processor = JsonLdExtractorProcessor()
        return [self._processor]
    
    def finalize(self) -> None:
        """Cleanup plugin resources."""
        self._processor = None