"""
Plugin Interface for DR Web Engine
Defines the contract for external plugins to extend engine functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .processors import StepProcessor


@dataclass
class PluginMetadata:
    """Metadata for DR Web Engine plugins."""
    name: str
    version: str
    description: str
    author: str
    homepage: Optional[str] = None
    supported_step_types: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    min_drweb_version: str = "0.10.0"
    enabled: bool = True
    
    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.name or not self.version:
            raise ValueError("Plugin name and version are required")
        if not self.author:
            raise ValueError("Plugin author is required")


class DrWebPlugin(ABC):
    """Base interface for DR Web Engine plugins.
    
    All plugins must implement this interface to be discoverable and loadable
    by the DR Web Engine plugin system.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata.
        
        Returns:
            PluginMetadata: Plugin information and configuration
        """
        pass
    
    @abstractmethod
    def get_processors(self) -> List[StepProcessor]:
        """Return list of step processors provided by this plugin.
        
        Returns:
            List[StepProcessor]: List of processors to register with the engine
        """
        pass
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.
        
        Called when the plugin is loaded. Use this to setup resources,
        validate configuration, etc.
        
        Args:
            config: Plugin configuration dictionary
            
        Raises:
            PluginInitializationError: If plugin fails to initialize
        """
        pass
    
    def finalize(self) -> None:
        """Cleanup plugin resources.
        
        Called when the plugin is unloaded or the engine shuts down.
        Use this to clean up resources, close connections, etc.
        """
        pass
    
    def validate_dependencies(self) -> bool:
        """Validate that plugin dependencies are available.
        
        Returns:
            bool: True if all dependencies are available
        """
        try:
            for dep in self.metadata.dependencies:
                __import__(dep)
            return True
        except ImportError:
            return False
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Return JSON schema for plugin configuration.
        
        Returns:
            Optional[Dict]: JSON schema for configuration validation, or None
        """
        return None


class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass


class PluginInitializationError(PluginError):
    """Raised when plugin fails to initialize."""
    pass


class PluginLoadError(PluginError):
    """Raised when plugin fails to load."""
    pass


class PluginDependencyError(PluginError):
    """Raised when plugin dependencies are missing."""
    pass


class PluginVersionError(PluginError):
    """Raised when plugin version is incompatible."""
    pass