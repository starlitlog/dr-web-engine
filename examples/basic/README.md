# Basic Examples

Simple extraction patterns perfect for beginners to learn DR Web Engine fundamentals.

## Examples

### `simple_extraction.json5`
**Purpose**: Extract quotes, authors, and tags from a simple static page  
**Site**: https://quotes.toscrape.com/  
**Demonstrates**: Basic XPath field extraction, text content retrieval  
**Run**: `dr-web-engine -q simple_extraction.json5 -o quotes.json`

### `pagination.json5`  
**Purpose**: Extract data across multiple pages using pagination  
**Site**: https://quotes.toscrape.com/  
**Demonstrates**: Multi-page data collection, pagination limits  
**Run**: `dr-web-engine -q pagination.json5 -o quotes_paginated.json`

## Key Concepts

- **XPath basics**: `//div[@class='quote']` selects all quote divs
- **Text extraction**: `.//span[@class='text']/text()` gets text content
- **Attribute extraction**: `./@href` gets href attribute values
- **Pagination**: `"@pagination": {"@xpath": "...", "@limit": 3}` follows next page links

## Learning Path

1. Start with `simple_extraction.json5` to understand basic field mapping
2. Try `pagination.json5` to see multi-page data collection
3. Modify the XPath selectors to extract different fields
4. Experiment with different websites using the same patterns