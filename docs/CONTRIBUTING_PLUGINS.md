# Contributing Plugins to DR Web Engine

Thank you for your interest in contributing to the DR Web Engine plugin ecosystem! This guide will help you create high-quality plugins that benefit the entire community.

## 🎯 Plugin Contribution Overview

There are two ways to contribute plugins:

1. **Community Plugins** - Independent packages published to PyPI
2. **Internal Plugins** - Contributions to the core engine (rare, by invitation)

This guide focuses on **Community Plugins** as they're the primary contribution method.

## 🚀 Quick Contribution Checklist

Before submitting your plugin to the registry:

- [ ] **Unique Functionality** - Plugin solves a real problem not addressed by existing plugins
- [ ] **Quality Code** - Follows Python best practices and DR Web Engine conventions
- [ ] **Comprehensive Tests** - Unit tests and integration tests with good coverage
- [ ] **Documentation** - Clear README, examples, and API documentation
- [ ] **Security** - No hardcoded secrets, proper input validation
- [ ] **PyPI Package** - Published with `drweb-plugin-` prefix
- [ ] **Semantic Versioning** - Proper version management
- [ ] **License** - Open source license (MIT, Apache 2.0, GPL, etc.)

## 📋 Detailed Contribution Guidelines

### 1. Plugin Planning & Design

#### Research Existing Solutions
```bash
# Search for similar plugins
drweb plugin search "your-functionality"

# Check the registry
# Review docs/PLUGIN_REGISTRY.md
```

#### Define Your Plugin's Scope
- **Single Responsibility** - One plugin, one purpose
- **Clear Use Cases** - Document specific scenarios where your plugin helps
- **Integration Points** - How it works with existing DR Web Engine features

#### Design Considerations
- **Performance** - Minimize resource usage
- **Compatibility** - Support DR Web Engine 0.10.0+
- **Extensibility** - Design for future enhancements
- **User Experience** - Simple configuration, clear error messages

### 2. Development Standards

#### Code Quality Requirements

**Python Standards:**
```python
# Type hints everywhere
def process_data(self, data: List[Dict[str, Any]]) -> List[ProcessedData]:
    """Process data with proper type hints."""
    pass

# Comprehensive docstrings
class MyProcessor(StepProcessor):
    """
    Process web data in an awesome way.
    
    This processor handles X, Y, and Z by doing A, B, and C.
    Useful for scenarios where you need to...
    
    Examples:
        Basic usage:
        >>> processor = MyProcessor()
        >>> results = processor.execute(context, page, step)
    """
```

**Error Handling:**
```python
def execute(self, context, page, step):
    try:
        # Main logic
        results = self._process_data(page, step)
        self.logger.info(f"Successfully processed {len(results)} items")
        return results
        
    except ValidationError as e:
        self.logger.warning(f"Invalid input: {e}")
        return []  # Graceful degradation
        
    except NetworkError as e:
        self.logger.error(f"Network issue: {e}")
        return []  # Don't crash the engine
        
    except Exception as e:
        self.logger.error(f"Unexpected error in {self.__class__.__name__}: {e}")
        return []  # Always return something
```

**Configuration Management:**
```python
class MyPlugin(DrWebPlugin):
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Return JSON schema for configuration validation."""
        return {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "API key for external service"
                },
                "max_retries": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 3
                }
            },
            "required": ["api_key"]
        }
```

#### Performance Requirements

**Resource Management:**
```python
class MyProcessor(StepProcessor):
    def __init__(self):
        super().__init__()
        self.connection_pool = None
        self.cache = {}
        self.cache_size_limit = 1000
    
    def initialize(self):
        """Initialize resources when plugin loads."""
        self.connection_pool = create_connection_pool()
    
    def finalize(self):
        """Clean up when plugin unloads."""
        if self.connection_pool:
            self.connection_pool.close()
        self.cache.clear()
```

**Caching Strategy:**
```python
import time
from functools import lru_cache

class MyProcessor(StepProcessor):
    def __init__(self):
        super().__init__()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _get_cached_result(self, key: str):
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return result
        return None
    
    def _set_cached_result(self, key: str, result):
        # Implement LRU eviction if needed
        if len(self.cache) > 1000:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (result, time.time())
```

### 3. Testing Requirements

#### Unit Tests (Required)
```python
# tests/test_my_processor.py
import pytest
from unittest.mock import Mock, patch
from my_awesome_plugin.processors.my_processor import MyProcessor, MyStep

class TestMyProcessor:
    @pytest.fixture
    def processor(self):
        return MyProcessor()
    
    @pytest.fixture
    def mock_page(self):
        page = Mock()
        page.url = "https://example.com"
        page.query_selector_all.return_value = []
        return page
    
    def test_can_handle_step(self, processor):
        step = MyStep(**{"@my-action": "test"})
        assert processor.can_handle(step)
    
    def test_execute_success(self, processor, mock_page):
        step = MyStep(**{"@my-action": "process"})
        results = processor.execute(None, mock_page, step)
        assert isinstance(results, list)
    
    def test_execute_error_handling(self, processor, mock_page):
        # Test that errors don't crash
        mock_page.query_selector_all.side_effect = Exception("Test error")
        step = MyStep(**{"@my-action": "process"})
        
        results = processor.execute(None, mock_page, step)
        assert results == []  # Should return empty list, not crash
```

#### Integration Tests (Recommended)
```python
# tests/test_integration.py
import pytest
from engine.web_engine.plugin_manager import PluginManager
from engine.web_engine.processors import StepProcessorRegistry

def test_plugin_loading():
    """Test that plugin loads correctly in DR Web Engine."""
    registry = StepProcessorRegistry()
    manager = PluginManager(registry)
    
    from my_awesome_plugin.plugin import MyAwesomePlugin
    plugin = MyAwesomePlugin()
    
    assert manager.load_plugin(plugin)
    assert "MyProcessor" in [p.__class__.__name__ for p in registry.get_processors()]

def test_end_to_end():
    """Test plugin works with actual web pages."""
    # Use a stable test site
    query = {
        "@url": "https://httpbin.org/html",
        "@steps": [
            {
                "@my-action": "process",
                "@target": "h1"
            }
        ]
    }
    
    # Test with real DR Web Engine
    # ... implementation depends on your specific plugin
```

### 4. Documentation Standards

#### Required Documentation

**README.md Template:**
```markdown
# My Awesome Plugin

Brief description of what your plugin does.

## Installation

```bash
pip install drweb-plugin-awesome
```

## Quick Start

```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@awesome-action": "process",
      "@target": "body"
    }
  ]
}
```

## Configuration

### Environment Variables
- `AWESOME_API_KEY` - Required API key
- `AWESOME_TIMEOUT` - Request timeout (default: 30)

### Plugin Configuration
```json5
{
  "@awesome-action": "process",
  "@target": ".content",
  "@options": {
    "max_items": 10,
    "include_metadata": true
  }
}
```

## Examples

### Basic Usage
[Include working examples]

### Advanced Usage
[Include complex scenarios]

## API Reference

### AwesomeStep
[Document your step model]

### Configuration Options
[Document all options]

## Error Handling

Common errors and solutions:
- Error X: Solution Y
- Error A: Solution B

## Contributing

How to contribute to your plugin.

## License

MIT License
```

**API Documentation:**
- Document all public classes and methods
- Include type hints and return types
- Provide usage examples
- Document configuration options

### 5. Security Requirements

#### Security Checklist
- [ ] **No Hardcoded Secrets** - Use environment variables or configuration
- [ ] **Input Validation** - Validate all user inputs
- [ ] **Safe Defaults** - Secure configuration by default
- [ ] **Dependency Security** - Regular dependency updates
- [ ] **Error Information** - Don't leak sensitive info in error messages

#### Security Best Practices
```python
import os
import re
from urllib.parse import urlparse

class SecureProcessor(StepProcessor):
    def __init__(self):
        super().__init__()
        # Get secrets from environment, not hardcoded
        self.api_key = os.getenv("MY_PLUGIN_API_KEY")
        if not self.api_key:
            raise ValueError("MY_PLUGIN_API_KEY environment variable required")
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL to prevent SSRF attacks."""
        try:
            parsed = urlparse(url)
            # Block internal networks
            if parsed.hostname in ['localhost', '127.0.0.1']:
                return False
            return parsed.scheme in ['http', 'https']
        except Exception:
            return False
    
    def _sanitize_input(self, user_input: str) -> str:
        """Sanitize user input."""
        # Remove dangerous characters
        return re.sub(r'[<>"\']', '', user_input)
```

### 6. Package Publishing

#### PyPI Publishing Checklist
- [ ] **Package Name** - Uses `drweb-plugin-` prefix
- [ ] **Version** - Follows semantic versioning
- [ ] **Metadata** - Proper classifiers and keywords
- [ ] **Dependencies** - Minimal and pinned versions
- [ ] **Entry Points** - Correct plugin registration
- [ ] **License File** - Include license file
- [ ] **Changelog** - Document version changes

#### Publishing Process
```bash
# 1. Update version
# Edit setup.py or pyproject.toml

# 2. Build package
python -m build

# 3. Test upload (optional)
twine upload --repository testpypi dist/*

# 4. Upload to PyPI
twine upload dist/*

# 5. Test installation
pip install drweb-plugin-yourname
drweb plugin list
```

### 7. Registry Submission

#### Pre-Submission Checklist
- [ ] Plugin published to PyPI
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Security review completed
- [ ] Examples tested

#### Submission Process
1. **Fork** the DR Web Engine repository
2. **Add** your plugin to `docs/PLUGIN_REGISTRY.md`
3. **Create PR** with plugin details
4. **Wait** for automated checks
5. **Address** any review feedback
6. **Celebrate** when approved! 🎉

#### Registry Entry Template
```markdown
### Your Plugin Name
- **Author:** [@yourusername](https://github.com/yourusername)
- **Description:** Brief description of functionality
- **Install:** `pip install drweb-plugin-yourname`
- **GitHub:** [repo-link](https://github.com/yourusername/drweb-plugin-yourname)
- **PyPI:** [pypi-link](https://pypi.org/project/drweb-plugin-yourname/)
- **Use Cases:** List of common use cases
- **Version:** 1.0.0
- **Status:** [![Tests](badge)](link) [![PyPI](badge)](link)
```

## 🔄 Ongoing Maintenance

### Version Management
- **Semantic Versioning** - MAJOR.MINOR.PATCH
- **Changelog** - Document all changes
- **Deprecation Notices** - Give users time to migrate
- **Security Updates** - Prompt security fixes

### Community Engagement
- **Issue Response** - Respond to issues within 48 hours
- **Feature Requests** - Consider community feedback
- **Documentation Updates** - Keep docs current
- **Compatibility** - Test with new DR Web Engine versions

## 🏆 Plugin Excellence Program

### Recognition Levels

**⭐ Community Plugin**
- Basic functionality working
- Listed in registry

**🌟 Quality Plugin**
- Comprehensive tests
- Great documentation
- Active maintenance

**💎 Featured Plugin**
- Exceptional quality
- Innovative functionality
- Community impact
- Featured prominently

### Benefits
- **Visibility** - Featured in documentation
- **Support** - Priority support from maintainers
- **Collaboration** - Opportunities to contribute to core
- **Recognition** - Community recognition and badges

## 🤝 Getting Help

### Before You Start
1. **Check existing plugins** - Avoid duplication
2. **Read the guides** - Review all documentation
3. **Plan your plugin** - Clear scope and goals

### During Development
- **GitHub Discussions** - Ask questions
- **Discord/Slack** - Real-time help (if available)
- **Example Plugins** - Study internal plugins

### After Publication
- **Plugin Registry PR** - Submit for listing
- **Community Feedback** - Gather user feedback
- **Continuous Improvement** - Regular updates

## 📞 Contact Information

- **General Questions:** [GitHub Discussions](https://github.com/starlitlog/dr-web-engine/discussions)
- **Plugin Issues:** [GitHub Issues](https://github.com/starlitlog/dr-web-engine/issues)
- **Security Reports:** security@drwebengine.com
- **Direct Contact:** maintainers@drwebengine.com

---

**Thank you for contributing to the DR Web Engine ecosystem!** Your plugins help make web scraping more accessible and powerful for everyone. 🚀