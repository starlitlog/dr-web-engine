# 📚 DR Web Engine Examples

This directory contains comprehensive examples organized by use case to help you get started with DR Web Engine quickly. Each category demonstrates different aspects of web data extraction.

## 📁 Directory Structure

```
examples/
├── basic/          # Simple extraction patterns for beginners
├── actions/        # Browser interaction examples  
├── ecommerce/      # E-commerce and marketplace extraction
├── news/           # News sites and blog extraction
├── social/         # Social media and forum extraction
├── advanced/       # Complex scenarios with conditionals and JavaScript
└── plugins/        # Plugin-specific examples (JSON-LD, API Extractor)
```

## 🚀 Getting Started

Choose examples based on your use case:

### For Beginners
Start with [basic/](basic/) examples to understand core concepts:
- `simple_extraction.json5` - Basic field extraction
- `pagination.json5` - Multi-page data collection

### For Dynamic Sites
Check [actions/](actions/) for browser interaction:
- `javascript_content.json5` - Wait for JavaScript-loaded content
- `infinite_scroll.json5` - Handle infinite scroll pages
- `form_interaction.json5` - Fill and submit forms
- `click_and_navigate.json5` - Click buttons and follow links

### For E-commerce
Use [ecommerce/](ecommerce/) patterns for online stores:
- `product_catalog.json5` - Extract product listings and details
- `childcare_services.json5` - Service directory extraction

### For News & Blogs
See [news/](news/) for article extraction:
- `blog_articles.json5` - Blog post and article content
- `libero_quotidiano.json5` - Italian news site with advanced XPath

### For Social Media
Check [social/](social/) for forum and social data:
- `reddit_posts.json5` - Reddit posts and comments
- `4chan_threads.json5` - Forum thread listings

### For Advanced Use Cases
Explore [advanced/](advanced/) for complex scenarios:
- `conditional_extraction.json5` - Branching logic based on content
- `javascript_execution.json5` - Custom JavaScript for data processing

### For Plugin Features
See [plugins/](plugins/) for latest capabilities:
- `jsonld_extraction.json5` - Structured data from JSON-LD
- `api_extraction.json5` - AJAX/REST API interception

## 🎯 Use Case Guide

### Basic Web Scraping
**Goal**: Extract static content from simple pages
**Examples**: `basic/simple_extraction.json5`
**Best for**: Product catalogs, article lists, directory sites

### Dynamic Content
**Goal**: Handle JavaScript-rendered content and interactions
**Examples**: `actions/javascript_content.json5`, `actions/infinite_scroll.json5`
**Best for**: SPAs, lazy-loaded content, AJAX sites

### E-commerce Data
**Goal**: Extract product information, prices, reviews
**Examples**: `ecommerce/product_catalog.json5`
**Best for**: Price monitoring, inventory tracking, market research

### News & Content
**Goal**: Extract articles, metadata, and structured content
**Examples**: `news/blog_articles.json5`, `news/libero_quotidiano.json5`
**Best for**: Content aggregation, news monitoring, research

### Social Media & Forums
**Goal**: Extract posts, comments, user interactions
**Examples**: `social/reddit_posts.json5`, `social/4chan_threads.json5`  
**Best for**: Social listening, sentiment analysis, community research

### Advanced Scenarios
**Goal**: Complex logic, conditionals, custom processing
**Examples**: `advanced/conditional_extraction.json5`, `advanced/javascript_execution.json5`
**Best for**: Multi-step workflows, data validation, custom transformations

### Modern Web APIs
**Goal**: Extract data from API calls and structured markup
**Examples**: `plugins/api_extraction.json5`, `plugins/jsonld_extraction.json5`
**Best for**: Modern SPAs, structured data, real-time content

## 🛠️ Running Examples

### Basic Usage
```bash
# Run any example
dr-web-engine -q examples/basic/simple_extraction.json5 -o results.json

# With debug logging
dr-web-engine -q examples/actions/infinite_scroll.json5 -o results.json -l debug

# Process multiple examples
for example in examples/basic/*.json5; do
  dr-web-engine -q "$example" -o "results_$(basename "$example" .json5).json"
done
```

### Custom Modifications
```bash
# Copy an example and modify for your needs
cp examples/ecommerce/product_catalog.json5 my_custom_query.json5
# Edit my_custom_query.json5 with your target URL and fields
dr-web-engine -q my_custom_query.json5 -o my_results.json
```

## 📖 Key Concepts Demonstrated

### XPath Patterns
- **Field extraction**: `".//span[@class='price']/text()"`
- **Attribute extraction**: `".//a/@href"`
- **Conditional XPath**: `".//span[@class='sale-price'] | .//span[@class='regular-price']"`
- **Text processing**: `"normalize-space(.)"`

### Browser Actions
- **Waiting**: `{"@type": "wait", "@until": "element", "@selector": ".content"}`
- **Clicking**: `{"@type": "click", "@selector": "button.load-more"}`
- **Scrolling**: `{"@type": "scroll", "@direction": "down", "@pixels": 500}`
- **Form filling**: `{"@type": "fill", "@selector": "input[name='email']", "@value": "test@example.com"}`

### Advanced Features
- **Conditionals**: `{"@if": {"@exists": ".premium"}, "@then": [...], "@else": [...]}`
- **Following links**: `{"@follow": {"@xpath": ".//a/@href", "@steps": [...]}}`
- **JavaScript execution**: `{"@javascript": "return document.title;", "@return-json": true}`
- **JSON-LD extraction**: `{"@json-ld": {"@schema": "Product", "@fields": ["name", "price"]}}`
- **API interception**: `{"@api": {"@endpoint": "/api/products", "@fields": ["id", "name"]}}`

## 🎨 Customization Tips

### Adapting Examples
1. **Change the URL**: Update `"@url"` to your target site
2. **Update XPath selectors**: Inspect the target page and modify field XPaths
3. **Add fields**: Include additional data points you need
4. **Adjust timeouts**: Increase timeouts for slow sites
5. **Add pagination**: Include `"@pagination"` for multi-page extraction

### Common Patterns
```json5
// Wait for dynamic content
"@actions": [
  {
    "@type": "wait",
    "@until": "element", 
    "@selector": ".dynamic-content",
    "@timeout": 10000
  }
]

// Extract with fallback selectors
"price": ".//span[@class='sale-price']/text() | .//span[@class='price']/text()"

// Follow links with depth control
"@follow": {
  "@xpath": ".//a[@class='details-link']/@href",
  "@max-depth": 2,
  "@steps": [...]
}
```

## 🔧 Troubleshooting

### Common Issues
- **Empty results**: Check XPath selectors with browser dev tools
- **Timeout errors**: Increase `@timeout` values for slow sites
- **Missing dynamic content**: Add appropriate `@wait` actions
- **Rate limiting**: Add delays between requests with `@wait` actions

### Debug Tips
```bash
# Enable debug logging
dr-web-engine -q example.json5 -o results.json -l debug

# Save debug logs to file
dr-web-engine -q example.json5 -o results.json -l debug --log-file debug.log

# Test XPath in browser console
$x("//div[@class='product']//span[@class='price']/text()")
```

## 📚 Further Learning

- **[Getting Started Guide](../GETTING_STARTED.md)**: Comprehensive tutorials
- **[README](../README.md)**: Full feature documentation  
- **[Query Keywords Reference](../README.md#-query-keywords-reference)**: Complete syntax guide
- **[Real-World Examples](../README.md#-real-world-examples)**: Production use cases

## 🤝 Contributing Examples

Have a useful example? We'd love to include it!

1. **Create your example** following the existing patterns
2. **Test thoroughly** on the target site
3. **Add documentation** explaining the use case
4. **Submit a PR** with your example

### Example Template
```json5
{
  // Brief description of what this example does
  "@url": "https://example.com",
  "@steps": [
    {
      "@xpath": "//selector",
      "@name": "descriptive_name",
      "@fields": {
        "field1": "xpath_expression",
        "field2": "xpath_expression"
      }
    }
  ]
}
```

---

<div align="center">

**Happy scraping! 🕷️**

For support, check our [GitHub Issues](https://github.com/starlitlog/dr-web-engine/issues) or [Discussions](https://github.com/starlitlog/dr-web-engine/discussions).

</div>