"""
Plugin Discovery System for DR Web Engine
Discovers and loads plugins from various sources (PyPI, local, git).
"""

import os
import sys
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

from .plugin_interface import DrWebPlugin, PluginError, PluginLoadError, PluginDependencyError

logger = logging.getLogger(__name__)


class PluginDiscovery:
    """Discovers and loads plugins from various sources."""
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """Initialize plugin discovery.
        
        Args:
            plugin_dirs: Additional directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or []
        self.discovered_plugins: Dict[str, DrWebPlugin] = {}
    
    def discover_all_plugins(self) -> List[DrWebPlugin]:
        """Discover plugins from all sources.
        
        Returns:
            List[DrWebPlugin]: All discovered plugins
        """
        plugins = []
        
        # Discover installed plugins (via pip)
        try:
            installed_plugins = self.discover_installed_plugins()
            plugins.extend(installed_plugins)
            logger.info(f"Discovered {len(installed_plugins)} installed plugins")
        except Exception as e:
            logger.warning(f"Failed to discover installed plugins: {e}")
        
        # Discover local plugins
        try:
            local_plugins = self.discover_local_plugins()
            plugins.extend(local_plugins)
            logger.info(f"Discovered {len(local_plugins)} local plugins")
        except Exception as e:
            logger.warning(f"Failed to discover local plugins: {e}")
        
        # Cache discovered plugins
        for plugin in plugins:
            self.discovered_plugins[plugin.metadata.name] = plugin
        
        return plugins
    
    def discover_installed_plugins(self) -> List[DrWebPlugin]:
        """Discover plugins installed via pip using entry points.
        
        Returns:
            List[DrWebPlugin]: Installed plugins
            
        Raises:
            PluginLoadError: If plugin loading fails
        """
        plugins = []
        
        if not pkg_resources:
            logger.warning("pkg_resources not available, skipping installed plugin discovery")
            return plugins
        
        try:
            for entry_point in pkg_resources.iter_entry_points('drweb.plugins'):
                try:
                    plugin_class = entry_point.load()
                    plugin = plugin_class()
                    
                    if not isinstance(plugin, DrWebPlugin):
                        logger.warning(f"Plugin {entry_point.name} does not implement DrWebPlugin interface")
                        continue
                    
                    # Validate dependencies
                    if not plugin.validate_dependencies():
                        logger.warning(f"Plugin {plugin.metadata.name} has missing dependencies")
                        continue
                    
                    plugins.append(plugin)
                    logger.info(f"Discovered installed plugin: {plugin.metadata.name} v{plugin.metadata.version}")
                
                except Exception as e:
                    logger.error(f"Failed to load plugin from entry point {entry_point.name}: {e}")
                    
        except Exception as e:
            raise PluginLoadError(f"Failed to discover installed plugins: {e}")
        
        return plugins
    
    def discover_local_plugins(self) -> List[DrWebPlugin]:
        """Discover plugins in local directories.
        
        Returns:
            List[DrWebPlugin]: Local plugins
        """
        plugins = []
        
        # Default plugin directories
        default_dirs = [
            os.path.expanduser("~/.drweb/plugins"),
            os.path.join(os.getcwd(), "plugins"),
            os.path.join(os.getcwd(), ".drweb", "plugins")
        ]
        
        search_dirs = default_dirs + self.plugin_dirs
        
        for plugin_dir in search_dirs:
            if not os.path.exists(plugin_dir):
                continue
                
            try:
                dir_plugins = self._scan_directory(plugin_dir)
                plugins.extend(dir_plugins)
                if dir_plugins:
                    logger.info(f"Found {len(dir_plugins)} plugins in {plugin_dir}")
            except Exception as e:
                logger.warning(f"Failed to scan plugin directory {plugin_dir}: {e}")
        
        return plugins
    
    def _scan_directory(self, directory: str) -> List[DrWebPlugin]:
        """Scan a directory for plugin files.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List[DrWebPlugin]: Found plugins
        """
        plugins = []
        plugin_path = Path(directory)
        
        # Look for Python files and packages
        for item in plugin_path.iterdir():
            try:
                if item.is_file() and item.suffix == '.py' and item.name != '__init__.py':
                    # Single file plugin
                    plugin = self._load_plugin_from_file(str(item))
                    if plugin:
                        plugins.append(plugin)
                        
                elif item.is_dir() and not item.name.startswith('.'):
                    # Package plugin
                    init_file = item / '__init__.py'
                    plugin_file = item / 'plugin.py'
                    
                    if init_file.exists() or plugin_file.exists():
                        plugin = self._load_plugin_from_package(str(item))
                        if plugin:
                            plugins.append(plugin)
                            
            except Exception as e:
                logger.warning(f"Failed to load plugin from {item}: {e}")
        
        return plugins
    
    def _load_plugin_from_file(self, file_path: str) -> Optional[DrWebPlugin]:
        """Load plugin from a single Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Optional[DrWebPlugin]: Loaded plugin or None
        """
        try:
            file_path = Path(file_path)
            module_name = f"drweb_plugin_{file_path.stem}"
            
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Look for plugin classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, DrWebPlugin) and 
                    attr != DrWebPlugin):
                    
                    plugin = attr()
                    logger.info(f"Loaded plugin from file {file_path}: {plugin.metadata.name}")
                    return plugin
            
            logger.warning(f"No plugin class found in {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load plugin from file {file_path}: {e}")
            return None
    
    def _load_plugin_from_package(self, package_path: str) -> Optional[DrWebPlugin]:
        """Load plugin from a Python package.
        
        Args:
            package_path: Path to package directory
            
        Returns:
            Optional[DrWebPlugin]: Loaded plugin or None
        """
        try:
            package_path = Path(package_path)
            package_name = f"drweb_plugin_{package_path.name}"
            
            # Add parent directory to Python path
            parent_dir = str(package_path.parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # Try to import the package
            try:
                module = importlib.import_module(package_path.name)
            except ImportError:
                # Try with full path
                spec = importlib.util.spec_from_file_location(
                    package_name, 
                    package_path / '__init__.py'
                )
                if not spec or not spec.loader:
                    return None
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[package_name] = module
                spec.loader.exec_module(module)
            
            # Look for plugin classes in the module
            plugin = self._find_plugin_class(module)
            if plugin:
                logger.info(f"Loaded plugin from package {package_path}: {plugin.metadata.name}")
                return plugin
            
            # If no plugin in __init__.py, try plugin.py
            plugin_file = package_path / 'plugin.py'
            if plugin_file.exists():
                plugin_spec = importlib.util.spec_from_file_location(
                    f"{package_name}.plugin", 
                    plugin_file
                )
                if plugin_spec and plugin_spec.loader:
                    plugin_module = importlib.util.module_from_spec(plugin_spec)
                    plugin_spec.loader.exec_module(plugin_module)
                    
                    plugin = self._find_plugin_class(plugin_module)
                    if plugin:
                        logger.info(f"Loaded plugin from package {package_path}: {plugin.metadata.name}")
                        return plugin
            
            logger.warning(f"No plugin class found in package {package_path}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load plugin from package {package_path}: {e}")
            return None
    
    def _find_plugin_class(self, module) -> Optional[DrWebPlugin]:
        """Find and instantiate plugin class in module.
        
        Args:
            module: Python module to search
            
        Returns:
            Optional[DrWebPlugin]: Plugin instance or None
        """
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, DrWebPlugin) and 
                attr != DrWebPlugin):
                
                try:
                    return attr()
                except Exception as e:
                    logger.error(f"Failed to instantiate plugin class {attr_name}: {e}")
                    continue
        
        return None
    
    def load_plugin_by_name(self, plugin_name: str) -> Optional[DrWebPlugin]:
        """Load a specific plugin by name.
        
        Args:
            plugin_name: Name of plugin to load
            
        Returns:
            Optional[DrWebPlugin]: Loaded plugin or None
        """
        # Check if already discovered
        if plugin_name in self.discovered_plugins:
            return self.discovered_plugins[plugin_name]
        
        # Try to discover all plugins if not found
        self.discover_all_plugins()
        return self.discovered_plugins.get(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin.
        
        Args:
            plugin_name: Name of plugin
            
        Returns:
            Optional[Dict]: Plugin information or None
        """
        plugin = self.load_plugin_by_name(plugin_name)
        if not plugin:
            return None
        
        metadata = plugin.metadata
        return {
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "author": metadata.author,
            "homepage": metadata.homepage,
            "supported_step_types": metadata.supported_step_types,
            "dependencies": metadata.dependencies,
            "min_drweb_version": metadata.min_drweb_version,
            "enabled": metadata.enabled,
            "processors": len(plugin.get_processors())
        }