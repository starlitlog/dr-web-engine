# Plugin Architecture Design

## Overview

The DR Web Engine plugin system allows third-party packages to extend the engine's capabilities by providing custom step processors. This document outlines the plugin architecture, interfaces, and development guidelines.

## Current State vs Target State

### Current State (v0.9.5)
- Hard-coded processor registration in `engine.py`
- Built-in processors: Extract, Conditional, JavaScript, JsonLD, API, AI-Selector
- No external plugin discovery or management

### Target State (v0.10.0)
- Dynamic plugin discovery and loading
- External plugin packages installable via PyPI
- Plugin management CLI commands
- Plugin configuration and lifecycle management
- Plugin marketplace/registry

## Architecture Components

### 1. Plugin Interface Specification

```python
# drweb_plugin_interface.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    homepage: Optional[str] = None
    supported_step_types: List[str] = None
    dependencies: List[str] = None
    min_drweb_version: str = "0.10.0"

class DrWebPlugin(ABC):
    """Base interface for DR Web Engine plugins."""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def get_processors(self) -> List[StepProcessor]:
        """Return list of step processors provided by this plugin."""
        pass
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass
    
    def finalize(self) -> None:
        """Cleanup plugin resources."""
        pass
```

### 2. Plugin Discovery Mechanism

```python
# plugin_discovery.py
import importlib
import pkg_resources
from typing import List, Dict

class PluginDiscovery:
    """Discovers and loads plugins from various sources."""
    
    def discover_installed_plugins(self) -> List[DrWebPlugin]:
        """Discover plugins installed via pip."""
        plugins = []
        for entry_point in pkg_resources.iter_entry_points('drweb.plugins'):
            plugin_class = entry_point.load()
            plugins.append(plugin_class())
        return plugins
    
    def discover_local_plugins(self, plugin_dirs: List[str]) -> List[DrWebPlugin]:
        """Discover plugins in local directories."""
        # Implementation for local plugin loading
        pass
    
    def load_plugin_from_package(self, package_name: str) -> DrWebPlugin:
        """Load specific plugin package."""
        # Implementation for loading specific plugins
        pass
```

### 3. Plugin Manager

```python
# plugin_manager.py
class PluginManager:
    """Manages plugin lifecycle and registration."""
    
    def __init__(self, registry: StepProcessorRegistry):
        self.registry = registry
        self.loaded_plugins: Dict[str, DrWebPlugin] = {}
        self.discovery = PluginDiscovery()
    
    def discover_and_load_plugins(self) -> None:
        """Discover and load all available plugins."""
        plugins = self.discovery.discover_installed_plugins()
        for plugin in plugins:
            self.load_plugin(plugin)
    
    def load_plugin(self, plugin: DrWebPlugin) -> bool:
        """Load a specific plugin."""
        try:
            plugin.initialize({})
            for processor in plugin.get_processors():
                self.registry.register(processor)
            self.loaded_plugins[plugin.metadata.name] = plugin
            return True
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin.metadata.name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin."""
        if plugin_name not in self.loaded_plugins:
            return False
        
        plugin = self.loaded_plugins[plugin_name]
        for processor in plugin.get_processors():
            self.registry.unregister(processor)
        plugin.finalize()
        del self.loaded_plugins[plugin_name]
        return True
    
    def list_plugins(self) -> Dict[str, PluginMetadata]:
        """List all loaded plugins."""
        return {name: plugin.metadata for name, plugin in self.loaded_plugins.items()}
```

## Plugin Package Structure

### Example Plugin Package Structure
```
drweb-plugin-custom/
├── setup.py
├── pyproject.toml
├── README.md
├── drweb_plugin_custom/
│   ├── __init__.py
│   ├── plugin.py
│   ├── processors/
│   │   ├── __init__.py
│   │   └── custom_processor.py
│   └── models/
│       ├── __init__.py
│       └── custom_steps.py
└── tests/
    ├── __init__.py
    └── test_plugin.py
```

### Example Plugin Implementation
```python
# drweb_plugin_custom/plugin.py
from drweb_plugin_interface import DrWebPlugin, PluginMetadata
from .processors import CustomProcessor

class CustomPlugin(DrWebPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="drweb-custom-processor",
            version="1.0.0",
            description="Custom data processor for special use cases",
            author="Plugin Developer",
            homepage="https://github.com/dev/drweb-plugin-custom",
            supported_step_types=["CustomStep"],
            dependencies=["requests", "beautifulsoup4"],
            min_drweb_version="0.10.0"
        )
    
    def get_processors(self) -> List[StepProcessor]:
        return [CustomProcessor()]
```

### Example setup.py
```python
from setuptools import setup, find_packages

setup(
    name="drweb-plugin-custom",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "dr-web-engine>=0.10.0",
        "requests",
        "beautifulsoup4"
    ],
    entry_points={
        'drweb.plugins': [
            'custom = drweb_plugin_custom.plugin:CustomPlugin',
        ],
    },
    # ... other setup parameters
)
```

## CLI Commands

### Plugin Management Commands
```bash
# List available plugins
drweb plugin list

# Install plugin from PyPI
drweb plugin install drweb-plugin-custom

# Install plugin from git
drweb plugin install git+https://github.com/dev/drweb-plugin-custom.git

# Install plugin from local path
drweb plugin install ./local-plugin/

# Uninstall plugin
drweb plugin uninstall drweb-plugin-custom

# Show plugin information
drweb plugin info drweb-plugin-custom

# Enable/disable plugins
drweb plugin enable drweb-plugin-custom
drweb plugin disable drweb-plugin-custom

# Search for plugins
drweb plugin search ml-extraction
```

## Migration Path

### Phase 1: Core Plugin System (v0.10.0)
1. Create plugin interface and discovery mechanism
2. Refactor existing processors to use plugin interface
3. Add basic CLI commands for plugin management
4. Update documentation

### Phase 2: External Plugin Support (v0.10.5)
1. Support for PyPI-installed plugins
2. Plugin configuration management
3. Enhanced CLI commands
4. Example plugin templates

### Phase 3: Plugin Ecosystem (v0.11.0)
1. Plugin marketplace/registry
2. Plugin testing and validation tools
3. Plugin development SDK
4. Community plugin gallery

## Plugin Development Guidelines

### Best Practices
1. **Single Responsibility**: Each plugin should focus on one specific functionality
2. **Error Handling**: Robust error handling to prevent breaking the main engine
3. **Configuration**: Support for user configuration via environment variables or config files
4. **Documentation**: Comprehensive documentation and examples
5. **Testing**: Unit tests and integration tests for all processors
6. **Dependencies**: Minimal dependencies, clearly specified
7. **Versioning**: Semantic versioning and compatibility specification

### Plugin Categories
1. **Data Processors**: Custom extraction and processing logic
2. **Authentication**: Login and session management
3. **Anti-Bot**: Captcha solving, bot detection bypass
4. **Output Formatters**: Custom output formats and transformations
5. **Integrations**: Third-party service integrations
6. **Analysis**: Data analysis and enrichment tools

### Security Considerations
1. **Sandboxing**: Consider sandboxing plugin execution
2. **Validation**: Validate plugin metadata and code quality
3. **Permissions**: Plugin permission system for sensitive operations
4. **Code Review**: Community code review for published plugins

## Example Plugins to Develop

### Built-in Plugin Conversions (v0.10.0)
- `drweb-plugin-ai-selector` - AI-powered element selection
- `drweb-plugin-jsonld` - JSON-LD extraction
- `drweb-plugin-api` - API integration

### Community Plugin Ideas
- `drweb-plugin-ml-classifier` - ML-based content classification
- `drweb-plugin-captcha-solver` - Automated captcha solving
- `drweb-plugin-proxy-rotator` - IP rotation and proxy management
- `drweb-plugin-scheduler` - Task scheduling and automation
- `drweb-plugin-monitoring` - Performance monitoring and alerts
- `drweb-plugin-database` - Database storage integrations

This architecture provides a solid foundation for a thriving plugin ecosystem while maintaining backward compatibility and ease of use.