# WebQL Training Data for CodeLlama

This directory contains comprehensive JSONL training datasets designed to train CodeLlama (or other code generation models) to help write WebQL queries and CLI commands for data extraction using DR Web Engine.

## 📊 Dataset Overview

**Total Training Examples: 121**

The training data is organized into 8 specialized categories, each targeting different aspects of WebQL and DR Web Engine usage:

### 📁 Dataset Files

| File | Examples | Description |
|------|----------|-------------|
| `webql_basic_queries.jsonl` | 9 | Basic WebQL query patterns and CLI commands |
| `webql_advanced_features.jsonl` | 9 | Advanced features: actions, conditionals, JavaScript, LLM formats |
| `webql_cli_commands.jsonl` | 19 | Command-line interface usage and options |
| `webql_xpath_patterns.jsonl` | 30 | XPath selector patterns and techniques |
| `webql_use_cases.jsonl` | 9 | Real-world use cases and industry applications |
| `webql_error_handling.jsonl` | 14 | Error handling, debugging, and troubleshooting |
| `webql_plugin_system.jsonl` | 17 | Plugin usage, configuration, and management |
| `webql_optimization.jsonl` | 14 | Performance optimization and best practices |
| **`webql_complete_training.jsonl`** | **121** | **Combined dataset with all examples** |

## 🎯 Training Objectives

The model should learn to:

1. **Generate WebQL Queries**: Create syntactically correct JSON5 queries for web data extraction
2. **CLI Command Construction**: Generate proper `drweb` command-line invocations  
3. **XPath Selector Writing**: Create efficient XPath expressions for element selection
4. **Feature Integration**: Combine multiple WebQL features (actions, conditionals, pagination)
5. **Error Handling**: Provide debugging guidance and error resolution strategies
6. **Optimization**: Suggest performance improvements and best practices

## 📚 Content Categories

### 1. Basic Queries (`webql_basic_queries.jsonl`)
- Simple extraction patterns
- Basic field mapping
- URL and selector specification
- Fundamental WebQL structure

**Example Training Pair:**
```json
{
  "instruction": "Write a basic WebQL query to extract quotes from quotes.toscrape.com",
  "input": "I want to extract quotes, authors, and tags from the quotes website", 
  "output": "{\n  \"@url\": \"https://quotes.toscrape.com\",\n  \"@steps\": [\n    {\n      \"@xpath\": \"//div[@class='quote']\",\n      \"@fields\": {\n        \"text\": \".//span[@class='text']/text()\",\n        \"author\": \".//small[@class='author']/text()\",\n        \"tags\": \".//div[@class='tags']//a/text()\"\n      }\n    }\n  ]\n}"
}
```

### 2. Advanced Features (`webql_advanced_features.jsonl`)
- Browser actions and dynamic content handling
- Conditional logic (`@if`, `@then`, `@else`)
- Link following with `@follow`
- JavaScript execution
- LLM training data formats

### 3. CLI Commands (`webql_cli_commands.jsonl`)
- Basic command execution
- Debug logging and troubleshooting
- Plugin management
- Batch processing and automation
- Docker and CI/CD integration

### 4. XPath Patterns (`webql_xpath_patterns.jsonl`)
- Text content extraction
- Attribute value extraction
- Class and ID selectors
- Position-based selection
- Complex XPath expressions with functions

### 5. Use Cases (`webql_use_cases.jsonl`)
- E-commerce product extraction
- News article collection
- Social media data gathering
- Financial data extraction
- Real estate listings
- Academic paper collection

### 6. Error Handling (`webql_error_handling.jsonl`)
- Timeout management
- Missing element handling
- Rate limiting strategies
- CAPTCHA detection
- Network error recovery

### 7. Plugin System (`webql_plugin_system.jsonl`)
- AI-powered element selection
- JSON-LD structured data extraction
- API interception and extraction
- Plugin configuration and management
- Smart retry and proxy rotation

### 8. Optimization (`webql_optimization.jsonl`)
- Large-scale extraction strategies
- Memory and performance optimization
- Selector efficiency
- Concurrent processing
- Cost optimization for cloud deployment

## 🔧 Training Format

Each training example follows the instruction-tuning format:

```json
{
  "instruction": "Clear description of what to generate",
  "input": "User request or context", 
  "output": "Expected WebQL query or CLI command"
}
```

This format is compatible with:
- **CodeLlama** fine-tuning
- **Alpaca** instruction tuning
- **Vicuna** conversation training
- **General instruction-following** model training

## 🚀 Usage Examples

### For CodeLlama Fine-tuning

```python
from datasets import load_dataset

# Load the training data
dataset = load_dataset('json', data_files='webql_complete_training.jsonl')

# Fine-tune CodeLlama
from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")

# Training loop implementation...
```

### For Inference Testing

```python
# Test the trained model
prompt = \"\"\"
Instruction: Write a WebQL query to extract product information from an e-commerce site
Input: Extract product names, prices, and images from a product listing page
Output:
\"\"\"

response = model.generate(prompt)
print(response)
```

## 📋 Data Quality Standards

All training examples include:

✅ **Syntactically Valid**: All JSON5 queries are properly formatted  
✅ **Realistic Scenarios**: Based on actual web extraction use cases  
✅ **Best Practices**: Follow WebQL optimization guidelines  
✅ **Error Handling**: Include defensive programming patterns  
✅ **Documentation**: Clear instructions and context  

## 🎯 Model Capabilities After Training

A model trained on this dataset should be able to:

1. **Generate Complete Queries**: Create full WebQL extraction queries from natural language descriptions
2. **Debug Issues**: Suggest solutions for common extraction problems
3. **Optimize Performance**: Recommend efficiency improvements
4. **Handle Edge Cases**: Generate robust queries with error handling
5. **Use Advanced Features**: Integrate plugins, actions, and conditionals
6. **CLI Proficiency**: Generate proper command-line invocations

## 🔄 Training Recommendations

### Data Augmentation
- **Shuffle examples** during training to prevent overfitting
- **Combine categories** for multi-task learning
- **Add negative examples** for better error detection

### Training Parameters
- **Learning Rate**: 2e-5 to 5e-5 for fine-tuning
- **Batch Size**: 4-8 depending on GPU memory
- **Epochs**: 3-5 for instruction tuning
- **Max Length**: 2048 tokens for complex queries

### Evaluation Metrics
- **Syntax Validity**: Percentage of generated queries that parse correctly
- **Execution Success**: Percentage that run without errors
- **Semantic Accuracy**: Whether generated queries match intent
- **Best Practice Adherence**: Following WebQL optimization guidelines

## 📈 Extension Opportunities

The training data can be extended with:

- **Multi-language Support**: Add examples for different natural languages
- **Domain-Specific Patterns**: Industry-specific extraction patterns
- **Advanced Plugins**: New plugin examples as they're developed
- **Real Website Examples**: More specific site extraction patterns
- **Performance Benchmarks**: Speed and efficiency optimization examples

## 🤝 Contributing

To add new training examples:

1. Follow the existing JSON format
2. Ensure examples are tested and working
3. Add clear, descriptive instructions
4. Include realistic use cases
5. Update this README with new categories

---

**Generated for DR Web Engine v1.0.1+**  
**Compatible with CodeLlama, Alpaca, Vicuna, and other instruction-tuned models**