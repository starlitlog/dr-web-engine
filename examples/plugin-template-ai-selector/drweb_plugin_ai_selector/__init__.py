"""
DR Web Engine AI-Selector Plugin

AI-powered element selector plugin that converts natural language descriptions 
to XPath selectors using configurable AI endpoints.
"""

__version__ = "1.0.0"
__author__ = "DR Web Engine Team"
__email__ = "support@drwebengine.com"

from .plugin import AISelectorPlugin
from .processor import AISelectorProcessor
from .config import AIConfig

__all__ = ["AISelectorPlugin", "AISelectorProcessor", "AIConfig"]