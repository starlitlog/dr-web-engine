# Changelog

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