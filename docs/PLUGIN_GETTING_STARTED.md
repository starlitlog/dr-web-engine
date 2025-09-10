# Getting Started with Plugin Development

Welcome to DR Web Engine plugin development! This guide will walk you through creating, testing, and sharing plugins with the community.

## Quick Overview

DR Web Engine supports two types of plugins:

1. **Internal Plugins** - Built into the engine, maintained by the core team
2. **External Plugins** - Community-contributed, distributed via PyPI or GitHub

## 🚀 Your First Plugin in 10 Minutes

### Step 1: Set up Development Environment

```bash
# Clone DR Web Engine
git clone https://github.com/starlitlog/dr-web-engine.git
cd dr-web-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Step 2: Create Plugin Structure

```bash
mkdir my-awesome-plugin
cd my-awesome-plugin

# Create plugin structure
mkdir -p my_awesome_plugin/{processors,models}
touch my_awesome_plugin/__init__.py
touch my_awesome_plugin/plugin.py
touch my_awesome_plugin/processors/__init__.py
touch my_awesome_plugin/processors/awesome_processor.py
touch setup.py
touch README.md
```

### Step 3: Implement Your Plugin

Create `my_awesome_plugin/plugin.py`:

```python
"""My Awesome Plugin for DR Web Engine."""

from typing import List, Dict, Any
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor
from .processors.awesome_processor import AwesomeProcessor

class MyAwesomePlugin(DrWebPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-awesome-plugin",
            version="1.0.0",
            description="Does something awesome with web data",
            author="Your Name",
            homepage="https://github.com/yourusername/my-awesome-plugin",
            supported_step_types=["AwesomeStep"],
            dependencies=["requests"],  # List any dependencies
            min_drweb_version="0.10.0"
        )
    
    def get_processors(self) -> List[StepProcessor]:
        return [AwesomeProcessor()]
```

Create `my_awesome_plugin/processors/awesome_processor.py`:

```python
"""Awesome data processor."""

from typing import Any, List, Dict
from engine.web_engine.processors import StepProcessor
from pydantic import BaseModel, Field

class AwesomeStep(BaseModel):
    """Custom step for awesome processing."""
    action: str = Field(alias="@awesome-action")
    target: str = Field(alias="@target", default="body")
    options: Dict[str, Any] = Field(default_factory=dict, alias="@options")

class AwesomeProcessor(StepProcessor):
    def __init__(self):
        super().__init__()
        self.priority = 45  # Lower numbers = higher priority
    
    def can_handle(self, step: Any) -> bool:
        return isinstance(step, AwesomeStep)
    
    def get_supported_step_types(self) -> List[str]:
        return ["AwesomeStep"]
    
    def execute(self, context: Any, page: Any, step: AwesomeStep) -> List[Any]:
        """Execute awesome processing logic."""
        results = []
        
        try:
            if step.action == "extract-awesome-data":
                # Your awesome extraction logic here
                elements = page.query_selector_all(step.target)
                
                for element in elements:
                    result = {
                        "text": element.text_content().strip(),
                        "awesome_score": self._calculate_awesome_score(element),
                        "metadata": {
                            "action": step.action,
                            "target": step.target
                        }
                    }
                    results.append(result)
            
        except Exception as e:
            self.logger.error(f"Awesome processing failed: {e}")
            return []
        
        self.logger.info(f"Processed {len(results)} awesome elements")
        return results
    
    def _calculate_awesome_score(self, element) -> float:
        """Calculate how awesome this element is."""
        text = element.text_content()
        # Simple awesome scoring algorithm
        return min(len(text) * 0.1, 10.0)
```

### Step 4: Create Package Configuration

Create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="my-awesome-plugin",
    version="1.0.0",
    description="Awesome plugin for DR Web Engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/my-awesome-plugin",
    packages=find_packages(),
    install_requires=[
        "dr-web-engine>=0.10.0",
        "requests>=2.25.0"
    ],
    entry_points={
        'drweb.plugins': [
            'awesome = my_awesome_plugin.plugin:MyAwesomePlugin',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10+",
    ],
    python_requires=">=3.10",
)
```

### Step 5: Test Your Plugin

Create a test query `test_awesome.json5`:

```json5
{
  "@url": "https://quotes.toscrape.com",
  "@steps": [
    {
      "@awesome-action": "extract-awesome-data",
      "@target": ".quote",
      "@options": {
        "include_score": true
      }
    }
  ]
}
```

Install and test:

```bash
# Install your plugin
pip install -e .

# Test plugin discovery
drweb plugin list

# Test your plugin
drweb run -q test_awesome.json5 -o results.json
```

## 📦 Publishing Your Plugin

### Option 1: PyPI Distribution (Recommended)

1. **Prepare for publishing:**

```bash
# Install build tools
pip install build twine

# Build your package
python -m build

# Test upload to TestPyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

2. **Users can then install with:**

```bash
pip install my-awesome-plugin
drweb plugin list  # Your plugin appears automatically
```

### Option 2: GitHub Distribution

Users can install directly from GitHub:

```bash
drweb plugin install git+https://github.com/yourusername/my-awesome-plugin.git
```

### Option 3: Local Development

For testing and development:

```bash
drweb plugin install /path/to/my-awesome-plugin/
```

## 🎯 Plugin Registration & Community

### Getting Your Plugin Listed

To get your plugin featured in the official DR Web Engine plugin registry:

1. **Create a high-quality plugin** with:
   - Clear documentation and examples
   - Comprehensive tests
   - Proper error handling
   - Semantic versioning

2. **Submit a Plugin Registry PR:**

Fork the DR Web Engine repository and create a PR adding your plugin to `docs/PLUGIN_REGISTRY.md`:

```markdown
## Community Plugins

### Data Processing
- **[my-awesome-plugin](https://github.com/yourusername/my-awesome-plugin)** by [@yourusername](https://github.com/yourusername)
  - **Description:** Does something awesome with web data
  - **Install:** `pip install my-awesome-plugin`
  - **Use Cases:** Data enrichment, custom processing
  - **Stars:** ![GitHub stars](https://img.shields.io/github/stars/yourusername/my-awesome-plugin)
```

3. **Plugin Review Process:**
   - Code quality review
   - Security assessment
   - Documentation completeness
   - Test coverage verification
   - Community feedback period

## 🏆 Plugin Categories & Ideas

### Popular Plugin Categories

#### **Authentication & Access**
- OAuth integrations
- Session management
- Captcha solving
- Cookie handling

#### **Data Processing**
- ML-based data classification
- Data validation and cleaning
- Format conversions
- Data enrichment

#### **Anti-Detection**
- Proxy rotation
- User-agent rotation
- Browser fingerprinting evasion
- Rate limiting

#### **Integrations**
- Database connectors (MongoDB, PostgreSQL, etc.)
- Cloud storage (AWS S3, Google Cloud, etc.)
- Messaging systems (Slack, Discord, etc.)
- Analytics platforms

#### **Output & Formats**
- Custom export formats
- Real-time streaming
- Data visualization
- Report generation

### Plugin Ideas for Contributors

**🌟 High-Impact Ideas:**
- **Visual Selector Plugin** - Select elements by clicking in a browser
- **Smart Retry Plugin** - Intelligent retry logic with backoff
- **Data Pipeline Plugin** - Connect multiple extraction jobs
- **Monitoring Plugin** - Health checks and alerting
- **Multi-language Plugin** - Handle different languages and encodings

**🔧 Technical Ideas:**
- **Headless Chrome Extensions** - Load browser extensions
- **Mobile Emulation** - Mobile device simulation
- **Screenshot Plugin** - Capture screenshots during extraction
- **Performance Plugin** - Measure extraction performance
- **A/B Testing Plugin** - Test different extraction strategies

## 📋 Plugin Development Best Practices

### Code Quality

1. **Follow Python Standards**
   - PEP 8 style guide
   - Type hints everywhere
   - Comprehensive docstrings
   - Clear variable names

2. **Error Handling**
   ```python
   def execute(self, context, page, step):
       try:
           # Your logic here
           return results
       except SpecificError as e:
           self.logger.warning(f"Specific issue: {e}")
           return []  # Graceful degradation
       except Exception as e:
           self.logger.error(f"Unexpected error: {e}")
           return []  # Don't crash the engine
   ```

3. **Logging Best Practices**
   ```python
   # Use appropriate log levels
   self.logger.debug("Detailed debugging info")
   self.logger.info("Important events")
   self.logger.warning("Recoverable issues")
   self.logger.error("Serious problems")
   ```

### Performance

1. **Caching**
   ```python
   class MyProcessor(StepProcessor):
       def __init__(self):
           super().__init__()
           self.cache = {}
           self.cache_ttl = 300  # 5 minutes
   ```

2. **Resource Management**
   ```python
   def finalize(self):
       """Clean up resources when plugin is unloaded."""
       if hasattr(self, 'connection'):
           self.connection.close()
       self.cache.clear()
   ```

3. **Async Support**
   ```python
   import asyncio
   from concurrent.futures import ThreadPoolExecutor
   
   async def async_operation(self, data):
       # Async processing logic
       pass
   ```

### Security

1. **Input Validation**
   ```python
   def execute(self, context, page, step):
       # Validate inputs
       if not isinstance(step.target, str):
           raise ValueError("Target must be a string")
       
       # Sanitize user inputs
       safe_target = self._sanitize_selector(step.target)
   ```

2. **Dependency Management**
   - Pin dependency versions
   - Regular security updates
   - Minimal dependencies

### Testing

1. **Unit Tests**
   ```python
   import pytest
   from unittest.mock import Mock
   
   def test_awesome_processor():
       processor = AwesomeProcessor()
       mock_page = Mock()
       mock_step = AwesomeStep(**{"@awesome-action": "test"})
       
       results = processor.execute(None, mock_page, mock_step)
       assert len(results) >= 0
   ```

2. **Integration Tests**
   ```python
   def test_plugin_integration():
       # Test with real DR Web Engine
       pass
   ```

## 🤝 Community Guidelines

### Plugin Naming
- Use descriptive names: `drweb-plugin-pdf-extractor`
- Follow naming convention: `drweb-plugin-{functionality}`
- Avoid generic names like `drweb-plugin-utils`

### Documentation
- **README.md** with installation and usage
- **Examples** directory with sample queries
- **API documentation** for public methods
- **Changelog** for version updates

### Licensing
- Use standard licenses (MIT, Apache 2.0, GPL)
- Include license file
- Respect dependencies' licenses

### Versioning
- Follow semantic versioning (semver)
- Document breaking changes
- Provide migration guides

## 🆘 Getting Help

### Resources
- **[Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)** - Comprehensive technical guide
- **[Plugin Architecture](PLUGIN_ARCHITECTURE.md)** - System design details
- **[Community Forum](https://github.com/starlitlog/dr-web-engine/discussions)** - Ask questions
- **[Example Plugins](../internal-plugins/)** - Reference implementations

### Support Channels
1. **GitHub Issues** - Bug reports and feature requests
2. **GitHub Discussions** - General questions and ideas
3. **Plugin Registry PRs** - Plugin submission reviews
4. **Discord/Slack** - Real-time community chat (if available)

### Contributing Back
- Submit improvements to plugin system
- Help review other plugins
- Write documentation and tutorials
- Report bugs and security issues

---

**Happy Plugin Development!** 🚀

Start small, test thoroughly, and share your awesome creations with the community!