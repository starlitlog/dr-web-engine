# DR Web Engine AI-Selector Plugin

AI-powered element selector plugin for DR Web Engine that converts natural language descriptions to XPath selectors.

## Features

- **Natural Language Selection**: Describe elements in plain English instead of writing XPath
- **Multiple AI Providers**: Support for OpenAI, Ollama, and other OpenAI-compatible APIs
- **Smart Caching**: Automatic caching of AI responses for better performance
- **Fallback Patterns**: Built-in fallback patterns when AI is unavailable
- **Easy Configuration**: Simple environment variable configuration

## Installation

```bash
pip install drweb-plugin-ai-selector
```

## Configuration

Set up your AI provider using environment variables:

### OpenAI (Recommended)
```bash
export AI_SELECTOR_ENDPOINT="https://api.openai.com/v1/chat/completions"
export AI_SELECTOR_API_KEY="sk-your-openai-key-here"
export AI_SELECTOR_MODEL="gpt-4o-mini"  # Best value option
```

### Local Ollama
```bash
export AI_SELECTOR_ENDPOINT="http://localhost:11434/api/chat"
export AI_SELECTOR_MODEL="llama3.2:3b"
# No API key needed for local
```

### Custom OpenAI-Compatible API
```bash
export AI_SELECTOR_ENDPOINT="https://your-api.com/v1/chat/completions"
export AI_SELECTOR_API_KEY="your-key"
export AI_SELECTOR_MODEL="your-model"
```

## Usage

Use the `@ai-select` step in your DR Web Engine queries:

### Basic Example
```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@ai-select": "product prices",
      "@name": "prices",
      "@max-results": 10
    }
  ]
}
```

### Advanced Example
```json5
{
  "@url": "https://news-site.com",
  "@steps": [
    {
      "@ai-select": "article headlines",
      "@name": "headlines"
    },
    {
      "@ai-select": "publication dates",
      "@name": "dates"
    },
    {
      "@ai-select": "author names",
      "@name": "authors"
    }
  ]
}
```

## Supported Descriptions

The AI-Selector works best with clear, descriptive language:

**Good Examples:**
- "product prices including discounts"
- "customer review text content"
- "navigation menu links"
- "social media post timestamps"

**Avoid:**
- "prices" (too vague)
- "the red button" (color-based descriptions)
- "stuff" (unclear descriptions)

## How It Works

1. **Page Analysis**: Extracts page structure and context
2. **AI Query**: Sends natural language description + page context to AI
3. **XPath Generation**: AI returns XPath selector
4. **Caching**: Results are cached for performance
5. **Fallback**: Falls back to pattern matching if AI fails

## Performance

- **First request**: 500-2000ms (AI call)
- **Cached request**: 10-50ms (local lookup)
- **Fallback request**: 50-100ms (pattern matching)

## Cost Optimization

- **Use gpt-4o-mini**: Cheapest OpenAI option (~$0.0003 per query)
- **Enable caching**: Enabled by default
- **Consider local models**: Ollama for high-volume usage
- **Specific descriptions**: More specific = fewer retries

## Supported AI Models

### OpenAI
- `gpt-4o-mini` - Best value (recommended)
- `gpt-4o` - Highest accuracy
- `gpt-4-turbo` - Legacy option

### Local Models (via Ollama)
- `llama3.2:3b` - Fast and lightweight
- `codellama:7b` - Better for technical content
- `mistral:7b` - Balanced performance

### Other Providers
- Together AI, Groq, Anyscale - Use OpenAI-compatible endpoints

## Error Handling

The plugin gracefully handles:
- API timeouts or errors
- Invalid AI responses  
- Missing API keys
- Network issues

In all cases, it falls back to pattern matching or returns empty results without breaking the extraction pipeline.

## Development

### Local Development
```bash
git clone https://github.com/starlitlog/drweb-plugin-ai-selector
cd drweb-plugin-ai-selector
pip install -e .
```

### Running Tests
```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

## Support

- [Documentation](https://drwebengine.com/docs/plugins/ai-selector)
- [GitHub Issues](https://github.com/starlitlog/drweb-plugin-ai-selector/issues)
- [Community Forum](https://drwebengine.com/community)