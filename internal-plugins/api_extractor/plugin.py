"""
API Extractor Plugin Implementation
"""

from typing import List, Dict, Any
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor
from engine.web_engine.plugins.api_extractor import ApiExtractorProcessor


class ApiExtractorPlugin(DrWebPlugin):
    """
    API Extractor plugin for making API calls during extraction.
    
    This internal plugin allows making API calls as part of the extraction
    pipeline, useful for enriching data or fetching additional information.
    """
    
    def __init__(self):
        self._processor = None
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="api-extractor",
            version="1.0.0",
            description="Makes API calls and processes responses during extraction",
            author="DR Web Engine Team",
            homepage="https://github.com/starlitlog/dr-web-engine",
            supported_step_types=["ApiStep"],
            dependencies=["requests"],
            min_drweb_version="0.10.0",
            enabled=True
        )
    
    def get_processors(self) -> List[StepProcessor]:
        """Return list of step processors provided by this plugin."""
        if not self._processor:
            self._processor = ApiExtractorProcessor()
        return [self._processor]
    
    def finalize(self) -> None:
        """Cleanup plugin resources."""
        self._processor = None