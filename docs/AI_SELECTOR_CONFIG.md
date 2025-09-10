# AI-Selector Configuration Guide

The AI-Selector plugin translates natural language descriptions to XPath selectors using configurable AI endpoints. This allows users to extract elements by describing what they want instead of writing complex selectors.

## Configuration

### Environment Variables

The simplest way to configure AI-Selector:

```bash
# OpenAI (recommended)
export AI_SELECTOR_ENDPOINT="https://api.openai.com/v1/chat/completions"
export AI_SELECTOR_API_KEY="sk-your-openai-key-here"
export AI_SELECTOR_MODEL="gpt-4o-mini"  # Best value (replaces gpt-3.5-turbo)

# Claude (Anthropic)
export AI_SELECTOR_ENDPOINT="https://api.anthropic.com/v1/messages"
export AI_SELECTOR_API_KEY="sk-ant-your-key-here"
export AI_SELECTOR_MODEL="claude-3-haiku-20240307"

# Local Ollama
export AI_SELECTOR_ENDPOINT="http://localhost:11434/api/chat"
export AI_SELECTOR_MODEL="llama2"
# No API key needed for local
```

### Supported Providers

#### 1. OpenAI
```bash
AI_SELECTOR_ENDPOINT="https://api.openai.com/v1/chat/completions"
AI_SELECTOR_API_KEY="sk-..."
AI_SELECTOR_MODEL="gpt-4o-mini"  # Best value (replaces gpt-3.5-turbo)
# Alternatives: "gpt-4o" (higher accuracy), "gpt-4-turbo" (legacy)
```

**Best for**: High accuracy, reliable results
**Cost**: ~$0.0003 per query (gpt-4o-mini)

#### 2. Local Ollama
```bash
AI_SELECTOR_ENDPOINT="http://localhost:11434/api/chat"
AI_SELECTOR_MODEL="llama2"  # or codellama, mistral
```

**Best for**: Privacy, no API costs
**Requirements**: Local Ollama installation

#### 3. Custom OpenAI-Compatible Endpoints
```bash
AI_SELECTOR_ENDPOINT="https://your-api.com/v1/chat/completions"
AI_SELECTOR_API_KEY="your-key"
AI_SELECTOR_MODEL="your-model"
```

**Examples**: Together AI, Anyscale, LocalAI, etc.

## Usage Examples

### Basic Natural Language Selection

```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@ai-select": "product prices",
      "@name": "prices"
    }
  ]
}
```

### With Result Limiting

```json5
{
  "@ai-select": "customer reviews",
  "@name": "reviews",
  "@max-results": 5
}
```

### Mixed with Traditional XPath

```json5
{
  "@url": "https://site.com",
  "@steps": [
    // Use AI for hard-to-target elements
    {
      "@ai-select": "promotional banner text",
      "@name": "promo"
    },
    // Use XPath for precise selection
    {
      "@xpath": "//div[@id='footer']",
      "@fields": {
        "copyright": ".//span[@class='copyright']/text()"
      }
    }
  ]
}
```

## How It Works

1. **Page Analysis**: Extracts page structure and context
2. **AI Query**: Sends natural language description + page context to AI
3. **XPath Generation**: AI returns XPath selector
4. **Caching**: Results are cached for performance
5. **Fallback**: Falls back to pattern matching if AI fails

## Performance & Caching

### Automatic Caching
- Selections are cached based on URL + description + page structure
- Cache automatically invalidates when page structure changes
- Reduces API calls and improves performance

### Cache Performance
```
First request:  500-2000ms (AI call)
Cached request: 10-50ms (local lookup)
```

## Fallback Behavior

If AI is unavailable or fails, the plugin falls back to pattern-based selection:

- "price" → `//span[contains(@class, 'price')] | //div[contains(@class, 'price')]`
- "title" → `//h1 | //h2[@class='title']`
- "button" → `//button | //a[contains(@class, 'btn')]`
- etc.

## Error Handling

The plugin gracefully handles:
- API timeouts or errors
- Invalid AI responses
- Missing API keys
- Network issues

In all cases, it either falls back to patterns or returns empty results without breaking the extraction pipeline.

## Cost Optimization

### For Low-Cost Usage
1. Use `gpt-4o-mini` (cheapest OpenAI option)
2. Cache is enabled by default
3. Fallback patterns reduce API calls
4. Consider local Ollama for high-volume usage

### For High Accuracy
1. Use `gpt-4o` for complex selections
2. Increase temperature for creative selections
3. Use longer context for ambiguous pages

## Setup Examples

### Docker with OpenAI
```bash
docker run -e AI_SELECTOR_API_KEY="sk-..." \
           -e AI_SELECTOR_MODEL="gpt-3.5-turbo" \
           -v $(pwd):/app/data \
           drweb/dr-web-engine \
           -q /app/data/query.json5 -o /app/data/results.json
```

### Local Development
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh
ollama run llama2

# Configure DR Web Engine
export AI_SELECTOR_ENDPOINT="http://localhost:11434/api/chat"
export AI_SELECTOR_MODEL="llama2"

# Run extraction
dr-web-engine -q ai_query.json5 -o results.json
```

### GitHub Actions
```yaml
env:
  AI_SELECTOR_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  AI_SELECTOR_MODEL: "gpt-3.5-turbo"

steps:
  - name: Extract data
    run: dr-web-engine -q query.json5 -o results.json
```

## Troubleshooting

### Common Issues

**1. Empty results with AI**
- Check API key is valid
- Verify endpoint URL
- Check if description is clear enough

**2. Slow performance**
- Ensure caching is working
- Use faster models (gpt-3.5-turbo vs gpt-4)
- Check network latency to AI endpoint

**3. High costs**
- Enable caching (default)
- Use local models for development
- Write more specific descriptions

### Debug Mode

Enable debug logging to see what's happening:
```bash
dr-web-engine -q query.json5 -o results.json -l debug
```

This shows:
- Cache hits/misses
- AI API calls and responses
- Fallback usage
- Generated XPath selectors

## Best Practices

### Writing Good Descriptions

**Good**:
- "product prices including any discounts"
- "customer review text content"
- "navigation menu links"

**Bad**:
- "prices" (too vague)
- "the thing with the stuff" (unclear)
- "red button" (better to use visual descriptions sparingly)

### When to Use AI-Selector

**Use AI-Selector for**:
- Dynamic content with changing class names
- Content without clear patterns
- Cross-site extraction with different structures
- Hard-to-target elements

**Use traditional XPath for**:
- Precise element targeting
- Complex nested selections
- Performance-critical applications
- Elements with stable, predictable structure

### Performance Tips

1. **Be specific**: "product title" vs "title"
2. **Use caching**: Same descriptions will reuse selectors
3. **Combine approaches**: AI for discovery, XPath for precision
4. **Limit results**: Use `@max-results` to avoid over-extraction

## Future Enhancements

Planned improvements:
- Visual descriptions using vision models
- Learning from user corrections
- Site-specific pattern learning
- Confidence scoring for selections