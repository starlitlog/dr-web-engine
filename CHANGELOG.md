# Changelog

## [0.10.0] - 2025-09-10

### Added - Plugin Ecosystem 🚀
- **Complete Plugin System**: Full plugin discovery, loading, and management
- **Plugin CLI Commands**: `drweb plugin list|install|uninstall|enable|disable|info`
- **Plugin Interface**: Standardized `DrWebPlugin` interface for external plugins
- **Plugin Discovery**: Automatic discovery from PyPI, Git, and local directories
- **Plugin Manager**: Lifecycle management with configuration support

### Plugin Architecture
- **Plugin Interface Specification**: Comprehensive `DrWebPlugin` base class
- **Step Processor Extension**: Extensible processor registration system  
- **Configuration Management**: JSON schema-based plugin configuration
- **Error Handling**: Graceful plugin failure handling and cleanup
- **Caching Support**: Built-in caching infrastructure for plugins

### Documentation
- **Plugin Development Guide**: Complete guide for creating plugins
- **Plugin Architecture Documentation**: Technical architecture overview
- **AI-Selector Plugin Example**: Full working example plugin package
- **Plugin Template**: Ready-to-use plugin template structure

### CLI Enhancements
- Rich console output with tables and colors
- Plugin management commands with detailed information
- JSON output support for programmatic usage
- Enhanced error messages and help text

### Dependencies
- Added `rich` for enhanced CLI experience
- Added `packaging` for version comparison
- Optional `pkg_resources` support for plugin discovery

### Breaking Changes
- Plugin system requires minimum Python 3.10
- New plugin interface for extensibility
- Enhanced step processor registry

---

## [0.9.5] - 2025-09-10

### Added
- **AI-Selector Plugin**: Natural language element selection using OpenAI-compatible APIs
  - Convert descriptions like "product prices" to XPath selectors
  - Support for OpenAI, local Ollama, and custom endpoints
  - Automatic caching and fallback patterns
  - Comprehensive model migration guide (deprecated gpt-3.5-turbo → gpt-4o-mini)
  
- **Enhanced Step Processing**: 
  - New `AiSelectStep` model with `@ai-select`, `@name`, and `@max-results` parameters
  - Improved step validation and error handling
  
- **Repository Organization**:
  - Organized all examples into `/examples` folder by use case
  - Categories: basic, actions, ecommerce, news, social, advanced, plugins
  - Comprehensive documentation and usage guides

- **Documentation**:
  - `docs/AI_SELECTOR_CONFIG.md` - Configuration guide
  - `docs/AI_MODEL_OPTIONS.md` - Model comparison and migration guide
  - `examples/plugins/ai_selector_simple.json5` - Usage examples

### Changed
- Updated default AI model from deprecated `gpt-3.5-turbo` to `gpt-4o-mini`
- Improved fallback patterns for better cross-site compatibility
- Enhanced error handling and logging

### Dependencies
- Added `requests` for AI API integration

### Examples
- Moved and organized 16+ example files into logical categories
- Added AI-Selector examples for common use cases

---

## [0.9.0] - Previous Release
- Core extraction engine
- Basic step processors
- XPath and CSS selector support