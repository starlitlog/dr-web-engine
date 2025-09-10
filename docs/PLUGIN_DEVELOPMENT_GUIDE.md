# Plugin Development Guide

Complete guide for developing plugins for DR Web Engine.

## Quick Start

### 1. Create Plugin Structure

```bash
mkdir my-drweb-plugin
cd my-drweb-plugin

# Create directory structure
mkdir -p my_drweb_plugin/{processors,models}
touch my_drweb_plugin/__init__.py
touch my_drweb_plugin/plugin.py
touch my_drweb_plugin/processors/__init__.py
touch setup.py
touch README.md
touch LICENSE
```

### 2. Implement Plugin Interface

```python
# my_drweb_plugin/plugin.py
from typing import List, Dict, Any, Optional
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor
from .processors.my_processor import MyCustomProcessor

class MyPlugin(DrWebPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-drweb-plugin",
            version="1.0.0",
            description="My custom DR Web Engine plugin",
            author="Your Name",
            homepage="https://github.com/yourusername/my-drweb-plugin",
            supported_step_types=["MyCustomStep"],
            dependencies=["requests"],
            min_drweb_version="0.10.0"
        )
    
    def get_processors(self) -> List[StepProcessor]:
        return [MyCustomProcessor()]
    
    def initialize(self, config: Dict[str, Any]) -> None:
        # Initialize your plugin with configuration
        pass
    
    def finalize(self) -> None:
        # Cleanup resources
        pass
```

### 3. Create Custom Processor

```python
# my_drweb_plugin/processors/my_processor.py
from typing import Any, List
from engine.web_engine.processors import StepProcessor
from engine.web_engine.models import BaseModel
from pydantic import Field

class MyCustomStep(BaseModel):
    """Custom step model."""
    action: str = Field(alias="@my-action")
    target: str = Field(alias="@target")

class MyCustomProcessor(StepProcessor):
    def __init__(self):
        super().__init__()
        self.priority = 50  # Lower = higher priority
    
    def can_handle(self, step: Any) -> bool:
        return isinstance(step, MyCustomStep)
    
    def get_supported_step_types(self) -> List[str]:
        return ["MyCustomStep"]
    
    def execute(self, context: Any, page: Any, step: MyCustomStep) -> List[Any]:
        # Implement your custom logic here
        results = []
        # ... processing logic ...
        return results
```

### 4. Create setup.py

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my-drweb-plugin",
    version="1.0.0",
    description="My custom DR Web Engine plugin",
    packages=find_packages(),
    install_requires=[
        "dr-web-engine>=0.10.0",
        "requests"
    ],
    entry_points={
        'drweb.plugins': [
            'my-plugin = my_drweb_plugin.plugin:MyPlugin',
        ],
    },
)
```

### 5. Install and Test

```bash
# Install in development mode
pip install -e .

# Test plugin discovery
drweb plugin list

# Test your plugin
drweb run -q my_query.json5 -o results.json
```

## Plugin Architecture

### Plugin Interface

All plugins must implement the `DrWebPlugin` interface:

```python
class DrWebPlugin(ABC):
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def get_processors(self) -> List[StepProcessor]:
        """Return processors provided by this plugin."""
        pass
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass
    
    def finalize(self) -> None:
        """Cleanup plugin resources."""
        pass
```

### Step Processor Interface

All processors must implement the `StepProcessor` interface:

```python
class StepProcessor(ABC):
    def __init__(self):
        self.priority = 100  # Lower = higher priority
    
    @abstractmethod
    def can_handle(self, step: Any) -> bool:
        """Check if this processor can handle the step."""
        pass
    
    @abstractmethod
    def execute(self, context: Any, page: Any, step: Any) -> List[Any]:
        """Execute the step and return results."""
        pass
    
    def get_supported_step_types(self) -> List[str]:
        """Return supported step types."""
        return []
```

## Step Model Development

### 1. Define Custom Step Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MyCustomStep(BaseModel):
    """Custom step for my plugin."""
    action: str = Field(alias="@my-action", description="Action to perform")
    target: str = Field(alias="@target", description="Target element")
    options: Optional[Dict[str, Any]] = Field(default=None, alias="@options")
    max_results: int = Field(default=10, alias="@max-results")
```

### 2. Register Step Model

```python
# In your plugin's models.py or __init__.py
from engine.web_engine.models import Step
from typing import Union

# Extend the Step union type (this is handled automatically by the plugin system)
MyStep = Union[Step, MyCustomStep]
```

### 3. Use in Queries

```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@my-action": "extract-data",
      "@target": "product-info",
      "@options": {
        "format": "json",
        "include_metadata": true
      },
      "@max-results": 20
    }
  ]
}
```

## Advanced Features

### Configuration Management

```python
class MyPlugin(DrWebPlugin):
    def initialize(self, config: Dict[str, Any]) -> None:
        # Handle plugin configuration
        self.api_key = config.get('api_key')
        self.endpoint = config.get('endpoint', 'https://default-api.com')
        self.timeout = config.get('timeout', 30)
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Return JSON schema for configuration validation."""
        return {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "API key for external service"
                },
                "endpoint": {
                    "type": "string", 
                    "description": "API endpoint URL",
                    "default": "https://default-api.com"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300
                }
            },
            "required": ["api_key"]
        }
```

### Error Handling

```python
class MyCustomProcessor(StepProcessor):
    def execute(self, context: Any, page: Any, step: MyCustomStep) -> List[Any]:
        try:
            # Your processing logic
            results = self._process_step(page, step)
            return results
        
        except ConnectionError as e:
            self.logger.error(f"Network error in {self.__class__.__name__}: {e}")
            return []  # Return empty results, don't crash
        
        except ValueError as e:
            self.logger.warning(f"Invalid data in {self.__class__.__name__}: {e}")
            return []
        
        except Exception as e:
            self.logger.error(f"Unexpected error in {self.__class__.__name__}: {e}")
            return []
```

### Caching

```python
class MyCustomProcessor(StepProcessor):
    def __init__(self):
        super().__init__()
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
    
    def execute(self, context: Any, page: Any, step: MyCustomStep) -> List[Any]:
        # Generate cache key
        cache_key = self._generate_cache_key(page.url, step)
        
        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                self.logger.info(f"Using cached result for {cache_key}")
                return cached_result
        
        # Process and cache result
        results = self._process_step(page, step)
        self.cache[cache_key] = (results, time.time())
        
        return results
```

### Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MyAsyncProcessor(StepProcessor):
    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def execute(self, context: Any, page: Any, step: MyCustomStep) -> List[Any]:
        # For CPU-bound tasks, use thread pool
        if step.action == "cpu-intensive":
            future = self.executor.submit(self._cpu_intensive_task, step)
            return future.result()
        
        # For I/O-bound tasks, use async
        if step.action == "io-bound":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._async_task(step))
            finally:
                loop.close()
        
        return []
```

## Plugin Categories & Examples

### 1. Data Extraction Plugins

```python
class DataExtractionProcessor(StepProcessor):
    """Extract structured data from pages."""
    
    def execute(self, context: Any, page: Any, step: DataExtractionStep) -> List[Any]:
        # Extract tables, lists, forms, etc.
        if step.data_type == "table":
            return self._extract_table_data(page, step.selector)
        elif step.data_type == "list":
            return self._extract_list_data(page, step.selector)
        # ... etc
```

### 2. Authentication Plugins

```python
class AuthProcessor(StepProcessor):
    """Handle login and session management."""
    
    def execute(self, context: Any, page: Any, step: AuthStep) -> List[Any]:
        if step.auth_type == "login":
            self._perform_login(page, step.username, step.password)
        elif step.auth_type == "oauth":
            self._handle_oauth_flow(page, step.provider)
        # ... etc
```

### 3. Anti-Bot Plugins

```python
class AntiBotProcessor(StepProcessor):
    """Handle captchas and bot detection."""
    
    def execute(self, context: Any, page: Any, step: AntiBotStep) -> List[Any]:
        if self._detect_captcha(page):
            if step.captcha_solver == "2captcha":
                self._solve_with_2captcha(page)
            elif step.captcha_solver == "anticaptcha":
                self._solve_with_anticaptcha(page)
        # ... etc
```

### 4. Output Format Plugins

```python
class OutputFormatProcessor(StepProcessor):
    """Transform output to different formats."""
    
    def execute(self, context: Any, page: Any, step: FormatStep) -> List[Any]:
        raw_data = step.input_data
        
        if step.format == "csv":
            return self._convert_to_csv(raw_data)
        elif step.format == "xlsx":
            return self._convert_to_xlsx(raw_data)
        elif step.format == "xml":
            return self._convert_to_xml(raw_data)
        # ... etc
```

## Testing Your Plugin

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from my_drweb_plugin.plugin import MyPlugin
from my_drweb_plugin.processors.my_processor import MyCustomProcessor

class TestMyPlugin:
    def test_metadata(self):
        plugin = MyPlugin()
        metadata = plugin.metadata
        assert metadata.name == "my-drweb-plugin"
        assert metadata.version == "1.0.0"
    
    def test_get_processors(self):
        plugin = MyPlugin()
        processors = plugin.get_processors()
        assert len(processors) == 1
        assert isinstance(processors[0], MyCustomProcessor)

class TestMyCustomProcessor:
    def test_can_handle(self):
        processor = MyCustomProcessor()
        # Test with mock steps
        # ...
    
    def test_execute(self):
        processor = MyCustomProcessor()
        # Test execution with mock page and step
        # ...
```

### Integration Tests

```python
def test_plugin_integration():
    """Test plugin works with DR Web Engine."""
    from engine.web_engine.plugin_manager import PluginManager
    from engine.web_engine.processors import StepProcessorRegistry
    
    # Setup
    registry = StepProcessorRegistry()
    manager = PluginManager(registry)
    
    # Load plugin
    plugin = MyPlugin()
    success = manager.load_plugin(plugin)
    assert success
    
    # Test processor registration
    processors = registry.get_processors()
    processor_names = [p.__class__.__name__ for p in processors]
    assert "MyCustomProcessor" in processor_names
```

## Publishing Your Plugin

### 1. Package Structure

```
my-drweb-plugin/
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── my_drweb_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   ├── processors/
│   │   ├── __init__.py
│   │   └── my_processor.py
│   └── models/
│       ├── __init__.py
│       └── my_models.py
├── tests/
│   ├── __init__.py
│   ├── test_plugin.py
│   └── test_processors.py
├── examples/
│   └── usage_examples.json5
└── docs/
    └── configuration.md
```

### 2. Publishing to PyPI

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (test first)
twine upload --repository testpypi dist/*
twine upload dist/*
```

### 3. GitHub Repository

- Include comprehensive README.md
- Add usage examples
- Provide configuration documentation
- Include CI/CD workflows
- Add issue templates

## Best Practices

### Code Quality

1. **Follow PEP 8** style guidelines
2. **Type hints** for all public methods
3. **Docstrings** for classes and methods
4. **Error handling** for all external calls
5. **Logging** instead of print statements

### Performance

1. **Minimize dependencies** - only include what you need
2. **Lazy loading** - import heavy modules only when needed
3. **Caching** - cache expensive operations
4. **Async/await** for I/O bound operations
5. **Connection pooling** for external APIs

### Security

1. **Input validation** - validate all user inputs
2. **API key management** - don't hardcode secrets
3. **Safe defaults** - secure configuration by default
4. **Dependency scanning** - check for vulnerabilities
5. **Permissions** - request minimal required permissions

### Documentation

1. **Clear README** with installation and usage
2. **API documentation** for public methods
3. **Configuration guide** with examples
4. **Troubleshooting section** for common issues
5. **Contributing guidelines** for open source

## Example Plugin Templates

### Basic Template
- Simple data extraction
- Environment-based configuration
- Basic error handling
- Minimal dependencies

### Advanced Template  
- Complex multi-step processing
- Database integration
- Async operations
- Comprehensive testing
- CI/CD pipeline

### AI/ML Template
- Machine learning integration
- GPU acceleration support
- Model management
- Performance monitoring
- Scalable architecture

## Community Guidelines

### Plugin Naming
- Use `drweb-plugin-` prefix
- Descriptive names (e.g., `drweb-plugin-pdf-extractor`)
- Avoid generic names

### Version Management
- Follow semantic versioning (semver)
- Document breaking changes
- Maintain backward compatibility when possible

### Support
- Provide issue templates
- Respond to user questions
- Maintain documentation
- Regular updates and bug fixes

## Resources

- [DR Web Engine Documentation](https://drwebengine.com/docs)
- [Plugin API Reference](https://drwebengine.com/docs/api)
- [Community Forum](https://drwebengine.com/community)
- [Example Plugins Repository](https://github.com/starlitlog/drweb-plugins)
- [Plugin Development Kit](https://github.com/starlitlog/drweb-plugin-sdk)