"""
Plugin Manager for DR Web Engine
Manages plugin lifecycle, loading, and registration with the step processor registry.
"""

import logging
import os
from typing import Dict, List, Optional, Set, Any
from packaging.version import Version, parse as parse_version

from .plugin_interface import (
    DrWebPlugin, 
    PluginMetadata, 
    PluginError, 
    PluginInitializationError,
    PluginLoadError,
    PluginDependencyError,
    PluginVersionError
)
from .plugin_discovery import PluginDiscovery
from .processors import StepProcessorRegistry

logger = logging.getLogger(__name__)

# Current DR Web Engine version for compatibility checking
CURRENT_VERSION = "0.10.0"


class PluginManager:
    """Manages plugin lifecycle and registration."""
    
    def __init__(self, registry: StepProcessorRegistry, config: Optional[Dict[str, Any]] = None):
        """Initialize plugin manager.
        
        Args:
            registry: Step processor registry
            config: Plugin configuration dictionary
        """
        self.registry = registry
        self.config = config or {}
        self.loaded_plugins: Dict[str, DrWebPlugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.disabled_plugins: Set[str] = set()
        self.discovery = PluginDiscovery()
        
        # Load disabled plugins from config
        disabled = self.config.get('disabled_plugins', [])
        if isinstance(disabled, list):
            self.disabled_plugins.update(disabled)
    
    def discover_and_load_plugins(self, auto_load: bool = True) -> Dict[str, bool]:
        """Discover and optionally load all available plugins.
        
        Args:
            auto_load: Whether to automatically load discovered plugins
            
        Returns:
            Dict[str, bool]: Plugin name -> load success mapping
        """
        logger.info("Starting plugin discovery...")
        
        try:
            plugins = self.discovery.discover_all_plugins()
            logger.info(f"Discovered {len(plugins)} plugins")
            
            results = {}
            if auto_load:
                for plugin in plugins:
                    success = self.load_plugin(plugin)
                    results[plugin.metadata.name] = success
            else:
                # Just validate plugins without loading
                for plugin in plugins:
                    try:
                        self._validate_plugin(plugin)
                        results[plugin.metadata.name] = True
                    except Exception as e:
                        logger.error(f"Plugin {plugin.metadata.name} validation failed: {e}")
                        results[plugin.metadata.name] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Plugin discovery failed: {e}")
            return {}
    
    def load_plugin(self, plugin: DrWebPlugin) -> bool:
        """Load a specific plugin.
        
        Args:
            plugin: Plugin instance to load
            
        Returns:
            bool: True if loaded successfully
        """
        plugin_name = plugin.metadata.name
        
        try:
            # Check if plugin is disabled
            if plugin_name in self.disabled_plugins:
                logger.info(f"Plugin {plugin_name} is disabled, skipping")
                return False
            
            # Check if already loaded
            if plugin_name in self.loaded_plugins:
                logger.warning(f"Plugin {plugin_name} is already loaded")
                return True
            
            # Validate plugin
            self._validate_plugin(plugin)
            
            # Get plugin configuration
            plugin_config = self.plugin_configs.get(plugin_name, {})
            
            # Initialize plugin
            logger.info(f"Initializing plugin: {plugin_name} v{plugin.metadata.version}")
            plugin.initialize(plugin_config)
            
            # Register processors
            processors = plugin.get_processors()
            for processor in processors:
                self.registry.register(processor)
                logger.info(f"Registered processor: {processor.__class__.__name__}")
            
            # Store loaded plugin
            self.loaded_plugins[plugin_name] = plugin
            
            logger.info(f"Successfully loaded plugin: {plugin_name} "
                       f"({len(processors)} processors)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            # Cleanup on failure
            try:
                self._cleanup_failed_plugin(plugin)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup plugin {plugin_name}: {cleanup_error}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin.
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            bool: True if unloaded successfully
        """
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"Plugin {plugin_name} is not loaded")
            return False
        
        try:
            plugin = self.loaded_plugins[plugin_name]
            
            # Unregister processors
            processors = plugin.get_processors()
            for processor in processors:
                self.registry.unregister(processor)
                logger.info(f"Unregistered processor: {processor.__class__.__name__}")
            
            # Finalize plugin
            plugin.finalize()
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]
            
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin.
        
        Args:
            plugin_name: Name of plugin to reload
            
        Returns:
            bool: True if reloaded successfully
        """
        if plugin_name in self.loaded_plugins:
            if not self.unload_plugin(plugin_name):
                return False
        
        # Rediscover the plugin
        plugin = self.discovery.load_plugin_by_name(plugin_name)
        if not plugin:
            logger.error(f"Plugin {plugin_name} not found for reload")
            return False
        
        return self.load_plugin(plugin)
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a disabled plugin.
        
        Args:
            plugin_name: Name of plugin to enable
            
        Returns:
            bool: True if enabled successfully
        """
        if plugin_name not in self.disabled_plugins:
            logger.info(f"Plugin {plugin_name} is already enabled")
            return True
        
        self.disabled_plugins.discard(plugin_name)
        
        # Try to load the plugin
        plugin = self.discovery.load_plugin_by_name(plugin_name)
        if plugin:
            return self.load_plugin(plugin)
        
        logger.warning(f"Plugin {plugin_name} enabled but not found")
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin.
        
        Args:
            plugin_name: Name of plugin to disable
            
        Returns:
            bool: True if disabled successfully
        """
        # Add to disabled set
        self.disabled_plugins.add(plugin_name)
        
        # Unload if currently loaded
        if plugin_name in self.loaded_plugins:
            return self.unload_plugin(plugin_name)
        
        logger.info(f"Plugin {plugin_name} disabled")
        return True
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all plugins with their status.
        
        Returns:
            Dict[str, Dict]: Plugin name -> plugin info mapping
        """
        result = {}
        
        # Include loaded plugins
        for name, plugin in self.loaded_plugins.items():
            metadata = plugin.metadata
            result[name] = {
                "name": metadata.name,
                "version": metadata.version,
                "description": metadata.description,
                "author": metadata.author,
                "homepage": metadata.homepage,
                "status": "loaded",
                "enabled": True,
                "processors": len(plugin.get_processors()),
                "supported_step_types": metadata.supported_step_types
            }
        
        # Include discovered but not loaded plugins
        for name, plugin in self.discovery.discovered_plugins.items():
            if name not in result:
                metadata = plugin.metadata
                status = "disabled" if name in self.disabled_plugins else "available"
                result[name] = {
                    "name": metadata.name,
                    "version": metadata.version,
                    "description": metadata.description,
                    "author": metadata.author,
                    "homepage": metadata.homepage,
                    "status": status,
                    "enabled": name not in self.disabled_plugins,
                    "processors": len(plugin.get_processors()),
                    "supported_step_types": metadata.supported_step_types
                }
        
        return result
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin.
        
        Args:
            plugin_name: Name of plugin
            
        Returns:
            Optional[Dict]: Plugin information or None if not found
        """
        # Check loaded plugins first
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            metadata = plugin.metadata
            processors = plugin.get_processors()
            
            return {
                "name": metadata.name,
                "version": metadata.version,
                "description": metadata.description,
                "author": metadata.author,
                "homepage": metadata.homepage,
                "status": "loaded",
                "enabled": True,
                "supported_step_types": metadata.supported_step_types,
                "dependencies": metadata.dependencies,
                "min_drweb_version": metadata.min_drweb_version,
                "processors": [
                    {
                        "name": p.__class__.__name__,
                        "priority": getattr(p, 'priority', 100),
                        "supported_types": p.get_supported_step_types()
                    }
                    for p in processors
                ],
                "configuration": self.plugin_configs.get(plugin_name, {})
            }
        
        # Check discovered plugins
        return self.discovery.get_plugin_info(plugin_name)
    
    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Configure a plugin.
        
        Args:
            plugin_name: Name of plugin to configure
            config: Configuration dictionary
            
        Returns:
            bool: True if configured successfully
        """
        try:
            # Validate configuration if plugin provides schema
            if plugin_name in self.loaded_plugins:
                plugin = self.loaded_plugins[plugin_name]
                schema = plugin.get_config_schema()
                if schema:
                    # TODO: Add JSON schema validation
                    pass
            
            # Store configuration
            self.plugin_configs[plugin_name] = config
            
            # If plugin is loaded, reinitialize with new config
            if plugin_name in self.loaded_plugins:
                plugin = self.loaded_plugins[plugin_name]
                plugin.initialize(config)
            
            logger.info(f"Configured plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure plugin {plugin_name}: {e}")
            return False
    
    def _validate_plugin(self, plugin: DrWebPlugin) -> None:
        """Validate a plugin before loading.
        
        Args:
            plugin: Plugin to validate
            
        Raises:
            PluginVersionError: If version is incompatible
            PluginDependencyError: If dependencies are missing
            PluginError: If validation fails
        """
        metadata = plugin.metadata
        
        # Check version compatibility
        min_version = parse_version(metadata.min_drweb_version)
        current_version = parse_version(CURRENT_VERSION)
        
        if current_version < min_version:
            raise PluginVersionError(
                f"Plugin {metadata.name} requires DR Web Engine >= {metadata.min_drweb_version}, "
                f"but current version is {CURRENT_VERSION}"
            )
        
        # Check dependencies
        if not plugin.validate_dependencies():
            missing_deps = []
            for dep in metadata.dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            raise PluginDependencyError(
                f"Plugin {metadata.name} has missing dependencies: {missing_deps}"
            )
        
        # Validate processors
        processors = plugin.get_processors()
        if not processors:
            logger.warning(f"Plugin {metadata.name} provides no processors")
        
        for processor in processors:
            if not hasattr(processor, 'can_handle') or not hasattr(processor, 'execute'):
                raise PluginError(
                    f"Processor {processor.__class__.__name__} does not implement required methods"
                )
    
    def _cleanup_failed_plugin(self, plugin: DrWebPlugin) -> None:
        """Cleanup a plugin that failed to load.
        
        Args:
            plugin: Plugin to cleanup
        """
        try:
            # Try to unregister any processors that might have been registered
            processors = plugin.get_processors()
            for processor in processors:
                try:
                    self.registry.unregister(processor)
                except Exception:
                    pass  # Ignore cleanup errors
            
            # Try to finalize the plugin
            plugin.finalize()
            
        except Exception as e:
            logger.error(f"Error during plugin cleanup: {e}")
    
    def shutdown(self) -> None:
        """Shutdown plugin manager and unload all plugins."""
        logger.info("Shutting down plugin manager...")
        
        # Unload all plugins
        plugin_names = list(self.loaded_plugins.keys())
        for plugin_name in plugin_names:
            try:
                self.unload_plugin(plugin_name)
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_name} during shutdown: {e}")
        
        logger.info("Plugin manager shutdown complete")