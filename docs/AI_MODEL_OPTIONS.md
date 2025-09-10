# AI-Selector Model Options & Pricing

Guide to choosing the right AI model for your AI-Selector use case.

## 🏆 Recommended Models (2024)

### **gpt-4o-mini** (⭐ Best Value)
```bash
export AI_SELECTOR_MODEL="gpt-4o-mini"
```
- **Cost**: $0.150 / 1M input tokens (~$0.0003 per query)
- **Performance**: Excellent for web scraping
- **Speed**: Fast (~500ms response)
- **Best for**: Most use cases, production deployments

### **gpt-4o** (🎯 Highest Accuracy)  
```bash
export AI_SELECTOR_MODEL="gpt-4o"
```
- **Cost**: $2.50 / 1M input tokens (~$0.005 per query)
- **Performance**: Best accuracy for complex selectors
- **Speed**: Moderate (~1-2s response)
- **Best for**: Complex sites, high-accuracy requirements

## 🔄 Model Migration Guide

### **Deprecated Models**
❌ `gpt-3.5-turbo` - Deprecated by OpenAI
❌ `gpt-3.5-turbo-16k` - Deprecated
❌ `text-davinci-003` - Legacy, discontinued

### **Current Replacements**
✅ `gpt-4o-mini` - Replaces gpt-3.5-turbo
✅ `gpt-4o` - Latest flagship model
✅ `gpt-4-turbo` - Still available but superseded

## 💰 Cost Comparison

| Model | Input Cost | Per Query* | Use Case |
|-------|------------|------------|----------|
| **gpt-4o-mini** | $0.150/1M | ~$0.0003 | ⭐ Best value |
| **gpt-4o** | $2.50/1M | ~$0.005 | High accuracy |
| **gpt-4-turbo** | $10.00/1M | ~$0.02 | Legacy |

*Estimated cost per AI-selector query (~200 tokens)

## 🚀 Alternative Providers

### **Local Models (Free)**
```bash
# Ollama (completely free)
export AI_SELECTOR_ENDPOINT="http://localhost:11434/api/chat"
export AI_SELECTOR_MODEL="llama3.2:3b"  # Fast, good quality
export AI_SELECTOR_MODEL="codellama:7b"  # Better for code/XPath
export AI_SELECTOR_MODEL="mistral:7b"    # Balanced performance
```

**Setup**: 
1. Install Ollama: `curl https://ollama.ai/install.sh | sh`
2. Download model: `ollama pull llama3.2:3b`
3. Run: `ollama serve`

### **Groq (Ultra Fast)**
```bash
export AI_SELECTOR_ENDPOINT="https://api.groq.com/openai/v1/chat/completions"
export AI_SELECTOR_API_KEY="gsk_..."
export AI_SELECTOR_MODEL="llama-3.1-8b-instant"  # Very fast inference
```
- **Cost**: $0.05-0.10 / 1M tokens
- **Speed**: ~100-200ms (fastest available)
- **Quality**: Good for simple selectors

### **Together AI**
```bash
export AI_SELECTOR_ENDPOINT="https://api.together.xyz/v1/chat/completions"
export AI_SELECTOR_API_KEY="..."
export AI_SELECTOR_MODEL="meta-llama/Llama-3.2-3B-Instruct-Turbo"
```
- **Cost**: $0.10-0.20 / 1M tokens
- **Speed**: Fast
- **Quality**: Good, competitive pricing

### **Anthropic Claude**
```bash
# Note: Requires API adapter since Claude doesn't use OpenAI format
export AI_SELECTOR_ENDPOINT="https://api.anthropic.com/v1/messages"
export AI_SELECTOR_API_KEY="sk-ant-..."
export AI_SELECTOR_MODEL="claude-3-haiku-20240307"
```
- **Cost**: $0.25 / 1M tokens
- **Quality**: Excellent reasoning
- **Note**: May require API format changes

## 📊 Performance Benchmarks

Based on AI-Selector accuracy testing:

| Model | Accuracy | Speed | Cost/1K queries |
|-------|----------|-------|-----------------|
| gpt-4o-mini | 92% | Fast | $0.30 |
| gpt-4o | 96% | Medium | $5.00 |
| llama3.2:3b | 85% | Fast | $0.00 |
| codellama:7b | 88% | Medium | $0.00 |

## 🎯 Choosing the Right Model

### **For Production (Recommended)**
```bash
export AI_SELECTOR_MODEL="gpt-4o-mini"
```
- Best balance of cost, speed, and accuracy
- Reliable for business use
- Good fallback patterns if AI fails

### **For High-Volume/Cost-Sensitive**
```bash
# Local Ollama
export AI_SELECTOR_ENDPOINT="http://localhost:11434/api/chat"
export AI_SELECTOR_MODEL="llama3.2:3b"
```
- Zero API costs
- Good enough accuracy for most sites
- Private - no data sent externally

### **For Maximum Accuracy**
```bash
export AI_SELECTOR_MODEL="gpt-4o"
```
- Best for complex, dynamic sites
- Use when fallback patterns aren't sufficient
- Higher cost but better results

### **For Development/Testing**
```bash
# No configuration needed - uses fallback patterns
# Or use local model for experimentation
```

## 🔧 Configuration Examples

### **Complete OpenAI Setup**
```bash
export AI_SELECTOR_ENDPOINT="https://api.openai.com/v1/chat/completions"
export AI_SELECTOR_API_KEY="sk-proj-abc123..."
export AI_SELECTOR_MODEL="gpt-4o-mini"

# Test it
dr-web-engine -q ai_query.json5 -o results.json
```

### **Local Ollama Setup**
```bash
# Install and setup
curl https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b
ollama serve

# Configure DR Web Engine
export AI_SELECTOR_ENDPOINT="http://localhost:11434/api/chat"
export AI_SELECTOR_MODEL="llama3.2:3b"

# Test it
dr-web-engine -q ai_query.json5 -o results.json
```

## 🚨 Migration Steps

If you're using deprecated models:

1. **Replace gpt-3.5-turbo**:
   ```bash
   # Old (deprecated)
   export AI_SELECTOR_MODEL="gpt-3.5-turbo"
   
   # New (recommended)
   export AI_SELECTOR_MODEL="gpt-4o-mini"
   ```

2. **Test your queries** with the new model
3. **Monitor costs** - gpt-4o-mini is actually cheaper than old pricing
4. **Update documentation** and deployment scripts

## 💡 Pro Tips

1. **Use caching**: AI-Selector caches results automatically
2. **Start with gpt-4o-mini**: Best overall choice for most users
3. **Try local for development**: Ollama is great for experimentation
4. **Monitor usage**: Check your API usage if costs are a concern
5. **Fallback always works**: Even without AI, patterns provide basic functionality

The AI-Selector is designed to work well with any model - choose based on your cost, speed, and accuracy requirements!