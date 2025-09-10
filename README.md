# DR Web Engine

<div align="center">

**Modern, Query-Based Web Data Retrieval Engine**

*Transform any website into a structured data API with simple JSON5/YAML queries*

[![PyPI version](https://badge.fury.io/py/dr-web-engine.svg)](https://badge.fury.io/py/dr-web-engine)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-103%20passed-brightgreen.svg)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Publish to PyPI](https://github.com/starlitlog/dr-web-engine/actions/workflows/publish.yml/badge.svg)](https://github.com/starlitlog/dr-web-engine/actions/workflows/publish.yml)
[![Build and Test](https://github.com/starlitlog/dr-web-engine/actions/workflows/python-app.yml/badge.svg)](https://github.com/starlitlog/dr-web-engine/actions/workflows/python-app.yml)
[![Docker Build](https://github.com/starlitlog/dr-web-engine/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/starlitlog/dr-web-engine/actions/workflows/docker-publish.yml)

</div>

---

**DR Web Engine** is a powerful, open-source data extraction engine that transforms web scraping from code-heavy scripts into simple, declarative queries. Define what you want to extract using JSON5 or YAML, and let the engine handle the complex browser automation and data extraction.

## 🚀 Key Features

- **🎯 Query-Based Extraction**: Define extractions in JSON5/YAML instead of writing scraping code
- **🤖 Browser Actions (NEW in v0.6+)**: Click, scroll, wait, fill forms - handle dynamic content
- **🧠 Conditional Logic (NEW in v0.7+)**: Smart branching based on page conditions and content
- **🕸️ Kleene Star Navigation (NEW in v0.8+)**: Recursive link following with cycle detection and depth control
- **🚀 JavaScript Execution (NEW in v0.9+)**: Execute custom JavaScript for complex scenarios and data extraction
- **📊 JSON-LD Extraction (NEW in v1.0+)**: Extract structured data from JSON-LD script tags
- **🌐 API Extractor (NEW in v1.0+)**: Intercept and extract data from AJAX/REST API calls
- **⚡ Playwright-Powered**: Reliable automation with modern browser engine
- **🌍 Universal**: Extract from any website - static or JavaScript-heavy SPAs
- **📊 Structured Output**: Get clean JSON data ready for analysis
- **🔧 CLI & Docker**: Run from command line or containerized environments
- **🧪 Thoroughly Tested**: 103 tests covering all functionality

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation) 
- [Basic Usage](#-basic-usage)
- [Action System](#-action-system-new)
- [Conditional Logic](#-conditional-logic-new)
- [Kleene Star Navigation](#-kleene-star-navigation-new)
- [JavaScript Execution](#-javascript-execution-new)
- [JSON-LD Extraction](#-json-ld-extraction-new)
- [API Extractor](#-api-extractor-new)
- [Query Keywords](#-query-keywords-reference)
- [CLI Reference](#-cli-reference)
- [Real-World Examples](#-real-world-examples)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

## 🚀 Quick Start

### 1. Install DR Web Engine
```bash
pip install dr-web-engine
```

### 2. Create a simple query (save as `quotes.json5`)
```json5
{
  "@url": "https://quotes.toscrape.com",
  "@steps": [
    {
      "@xpath": "//div[@class='quote']",
      "@fields": {
        "text": ".//span[@class='text']/text()",
        "author": ".//small[@class='author']/text()",
        "tags": ".//div[@class='tags']//a/text()"
      }
    }
  ]
}
```

### 3. Run the extraction
```bash
dr-web-engine -q quotes.json5 -o results.json
```

### 4. Get structured data
```json
[
  {
    "text": "The world as we have created it is a process of our thinking...",
    "author": "Albert Einstein", 
    "tags": ["change", "deep-thoughts", "thinking", "world"]
  }
]
```

### 5. Explore more examples
Check out our comprehensive [examples directory](examples/) with organized use cases:
- **[Basic patterns](examples/basic/)**: Simple extraction for beginners
- **[Browser actions](examples/actions/)**: Dynamic content and interactions  
- **[E-commerce](examples/ecommerce/)**: Product catalogs and marketplaces
- **[News & blogs](examples/news/)**: Article and content extraction
- **[Social media](examples/social/)**: Forums and social platforms
- **[Advanced features](examples/advanced/)**: Conditionals and JavaScript
- **[Plugin examples](examples/plugins/)**: JSON-LD and API extraction

## 📦 Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install dr-web-engine
```

### Option 2: Install from Source
```bash
git clone https://github.com/starlitlog/dr-web-engine.git
cd dr-web-engine
pip install -e .
```

### Option 3: Docker
```bash
# Pull and run
docker run -v $(pwd)/data:/app/data drweb/dr-web-engine -q /app/data/query.json5 -o /app/data/output.json

# Or build locally
docker build -t dr-web-engine .
```

### Install Playwright Browsers (Required)
```bash
playwright install
```

## 💡 Basic Usage

### Simple Extraction
Extract data using XPath selectors:

```json5
{
  "@url": "https://news.ycombinator.com",
  "@steps": [
    {
      "@xpath": "//tr[@class='athing']",
      "@fields": {
        "title": ".//span[@class='titleline']/a/text()",
        "url": ".//span[@class='titleline']/a/@href",
        "rank": ".//span[@class='rank']/text()"
      }
    }
  ]
}
```

### With Pagination
Handle multi-page results:

```json5
{
  "@url": "https://quotes.toscrape.com",
  "@steps": [
    {
      "@xpath": "//div[@class='quote']",
      "@fields": {
        "text": ".//span[@class='text']/text()",
        "author": ".//small[@class='author']/text()"
      }
    }
  ],
  "@pagination": {
    "@xpath": "//li[@class='next']/a",
    "@limit": 3
  }
}
```

## 🎬 Action System (NEW)

Handle dynamic, JavaScript-heavy websites with browser actions executed before data extraction:

### JavaScript Site with Actions
```json5
{
  "@url": "https://quotes.toscrape.com/js/",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".quote",
      "@timeout": 10000
    },
    {
      "@type": "scroll", 
      "@direction": "down",
      "@pixels": 500
    },
    {
      "@type": "wait",
      "@until": "timeout",
      "@timeout": 2000
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='quote']",
      "@fields": {
        "text": ".//span[@class='text']/text()",
        "author": ".//small[@class='author']/text()"
      }
    }
  ]
}
```

### Form Interaction
Fill forms and submit them:

```json5
{
  "@url": "https://example-search.com",
  "@actions": [
    {
      "@type": "fill",
      "@selector": "input[name='search']", 
      "@value": "data extraction"
    },
    {
      "@type": "click",
      "@selector": "button[type='submit']"
    },
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".search-results",
      "@timeout": 10000
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='result']",
      "@fields": {
        "title": ".//h3/text()",
        "url": ".//a/@href"
      }
    }
  ]
}
```

### Supported Action Types

| Action | Purpose | Example |
|--------|---------|---------|
| **click** | Click buttons, links | `{"@type": "click", "@selector": "#load-more"}` |
| **scroll** | Scroll page or elements | `{"@type": "scroll", "@direction": "down", "@pixels": 500}` |
| **wait** | Wait for conditions | `{"@type": "wait", "@until": "element", "@selector": ".loaded"}` |
| **fill** | Fill form fields | `{"@type": "fill", "@selector": "input", "@value": "text"}` |
| **hover** | Hover over elements | `{"@type": "hover", "@selector": ".dropdown-menu"}` |
| **javascript** | Execute custom JavaScript | `{"@type": "javascript", "@code": "window.loadMore();"}` |

## 🧠 Conditional Logic (NEW)

Extract different data based on page conditions with smart branching logic:

### Premium vs Free Content Detection
```json5
{
  "@url": "https://news-site.com/article/123",
  "@steps": [
    {
      "@if": {"@exists": "#premium-content"},
      "@then": [
        {
          "@xpath": "//div[@class='premium-article']",
          "@fields": {
            "title": ".//h1/text()",
            "full_content": ".//div[@class='content']/text()",
            "premium_features": ".//div[@class='extras']/text()"
          }
        }
      ],
      "@else": [
        {
          "@xpath": "//div[@class='free-article']", 
          "@fields": {
            "title": ".//h1/text()",
            "preview": ".//div[@class='preview']/text()",
            "paywall_message": ".//div[@class='paywall']/text()"
          }
        }
      ]
    }
  ]
}
```

### Authentication State Detection
```json5
{
  "@url": "https://forum.example.com",
  "@steps": [
    {
      "@if": {"@exists": ".user-menu"},
      "@then": [
        {
          "@xpath": "//div[@class='authenticated-content']",
          "@fields": {
            "username": ".//span[@class='username']/text()",
            "private_messages": ".//div[@class='messages']/text()",
            "user_settings": ".//a[@class='settings']/@href"
          }
        }
      ],
      "@else": [
        {
          "@xpath": "//div[@class='guest-content']",
          "@fields": {
            "login_prompt": ".//div[@class='login-required']/text()",
            "signup_link": ".//a[@class='signup']/@href"
          }
        }
      ]
    }
  ]
}
```

### Search Results with Fallback
```json5
{
  "@url": "https://search-engine.com/search?q=query",
  "@steps": [
    {
      "@if": {"@min-count": 1, "@selector": ".search-result"},
      "@then": [
        {
          "@xpath": "//div[@class='search-result']",
          "@fields": {
            "title": ".//h3/text()",
            "url": ".//a/@href",
            "snippet": ".//p[@class='description']/text()"
          }
        }
      ],
      "@else": [
        {
          "@xpath": "//div[@class='no-results']",
          "@fields": {
            "message": ".//text()",
            "suggestions": ".//div[@class='suggestions']//a/text()"
          }
        }
      ]
    }
  ]
}
```

### Supported Condition Types

| Condition | Purpose | Example |
|-----------|---------|---------|
| **@exists** | Element exists check | `{"@exists": "#premium-section"}` |
| **@not-exists** | Element absence check | `{"@not-exists": ".advertisement"}` |
| **@contains** | Text content check | `{"@contains": "Premium Content"}` |
| **@count** | Exact element count | `{"@count": 3, "@selector": ".item"}` |
| **@min-count** | Minimum count check | `{"@min-count": 1, "@selector": ".result"}` |
| **@max-count** | Maximum count check | `{"@max-count": 10, "@selector": ".item"}` |

## 🕸️ Kleene Star Navigation (NEW)

Navigate and extract data recursively through multiple levels of links with cycle detection and depth control:

### Multi-Level Link Following
Extract data by following links recursively with the enhanced `@follow` system:

```json5
{
  "@url": "https://news-site.com",
  "@steps": [
    {
      "@xpath": "//div[@class='category-section']",
      "@fields": {
        "category": ".//h2/text()"
      },
      "@follow": {
        "@xpath": ".//a[@class='article-link']/@href",
        "@max-depth": 2,
        "@detect-cycles": true,
        "@follow-external": false,
        "@steps": [
          {
            "@xpath": "//article",
            "@fields": {
              "title": ".//h1/text()",
              "content": ".//div[@class='article-body']/text()",
              "author": ".//span[@class='author']/text()",
              "date": ".//time/@datetime"
            }
          }
        ]
      }
    }
  ]
}
```

### Forum Thread Navigation
Navigate through forum discussions with nested replies:

```json5
{
  "@url": "https://forum.example.com/threads/123",
  "@steps": [
    {
      "@xpath": "//div[@class='thread-post']",
      "@fields": {
        "post_content": ".//div[@class='post-body']/text()",
        "author": ".//span[@class='author']/text()",
        "timestamp": ".//time/@datetime"
      },
      "@follow": {
        "@xpath": ".//a[contains(@class, 'reply-link')]/@href",
        "@max-depth": 3,
        "@detect-cycles": true,
        "@steps": [
          {
            "@xpath": "//div[@class='reply']",
            "@fields": {
              "reply_content": ".//div[@class='reply-body']/text()",
              "reply_author": ".//span[@class='reply-author']/text()",
              "reply_time": ".//time/@datetime"
            }
          }
        ]
      }
    }
  ]
}
```

### E-commerce Category Crawling
Navigate through product categories and subcategories:

```json5
{
  "@url": "https://shop.example.com/categories",
  "@steps": [
    {
      "@xpath": "//div[@class='main-category']",
      "@fields": {
        "main_category": ".//h2/text()"
      },
      "@follow": {
        "@xpath": ".//a[@class='subcategory-link']/@href",
        "@max-depth": 3,
        "@detect-cycles": true,
        "@follow-external": false,
        "@steps": [
          {
            "@xpath": "//div[@class='product-card']",
            "@fields": {
              "product_name": ".//h3/text()",
              "price": ".//span[@class='price']/text()",
              "rating": ".//div[@class='rating']/@data-rating",
              "image": ".//img/@src"
            }
          }
        ]
      }
    }
  ]
}
```

### Wikipedia Article Chain
Follow related links in Wikipedia articles:

```json5
{
  "@url": "https://en.wikipedia.org/wiki/Machine_Learning",
  "@steps": [
    {
      "@xpath": "//div[@id='content']",
      "@fields": {
        "title": ".//h1/text()",
        "summary": ".//div[@class='mw-parser-output']/p[1]/text()"
      },
      "@follow": {
        "@xpath": ".//div[@class='mw-parser-output']//a[starts-with(@href, '/wiki/')]/@href",
        "@max-depth": 2,
        "@detect-cycles": true,
        "@follow-external": false,
        "@steps": [
          {
            "@xpath": "//div[@id='content']",
            "@fields": {
              "related_title": ".//h1/text()",
              "related_summary": ".//div[@class='mw-parser-output']/p[1]/text()"
            }
          }
        ]
      }
    }
  ]
}
```

### Follow Configuration Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `@max-depth` | Maximum recursion depth | 3 | `"@max-depth": 5` |
| `@detect-cycles` | Prevent infinite loops | true | `"@detect-cycles": false` |
| `@follow-external` | Follow external domains | false | `"@follow-external": true` |

## 📖 Query Keywords Reference

### Core Keywords
| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@url` | ✅ | Target URL to scrape | `"@url": "https://example.com"` |
| `@steps` | ✅ | Extraction steps | `"@steps": [...]` |
| `@xpath` | ✅ | XPath selector for elements | `"@xpath": "//div[@class='item']"` |
| `@fields` | ✅ | Field definitions | `"@fields": {"title": ".//h2/text()"}` |

### Optional Keywords
| Keyword | Description | Example |
|---------|-------------|---------|
| `@name` | Name for data group | `"@name": "products"` |
| `@actions` | Browser actions (v0.6+) | `"@actions": [...]` |
| `@pagination` | Pagination config | `"@pagination": {"@xpath": "//a[@class='next']"}` |
| `@limit` | Page limit | `"@limit": 5` |
| `@follow` | Follow links (Kleene star support) | `"@follow": {"@xpath": ".//a/@href", "@steps": [...]}` |

### Action Keywords (v0.6+)
| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@type` | ✅ | Action type | `"@type": "click"` |
| `@selector` | ❌ | CSS selector | `"@selector": "#button"` |
| `@xpath` | ❌ | XPath selector | `"@xpath": "//button[@id='btn']"` |
| `@until` | ❌ | Wait condition | `"@until": "element"` |
| `@timeout` | ❌ | Timeout (ms) | `"@timeout": 5000` |
| `@direction` | ❌ | Scroll direction | `"@direction": "down"` |
| `@pixels` | ❌ | Scroll distance | `"@pixels": 500` |
| `@value` | ❌ | Form field value | `"@value": "search term"` |

### Conditional Keywords (v0.7+)
| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@if` | ✅ | Condition to evaluate | `"@if": {"@exists": "#premium"}` |
| `@then` | ✅ | Steps if condition true | `"@then": [...]` |
| `@else` | ❌ | Steps if condition false | `"@else": [...]` |
| `@exists` | ❌ | Element exists check | `"@exists": "#element-id"` |
| `@not-exists` | ❌ | Element absence check | `"@not-exists": ".popup"` |
| `@contains` | ❌ | Text content check | `"@contains": "Premium Content"` |
| `@count` | ❌ | Exact element count | `"@count": 3` |
| `@min-count` | ❌ | Minimum count check | `"@min-count": 1` |
| `@max-count` | ❌ | Maximum count check | `"@max-count": 10` |

### Follow Keywords (v0.8+)
| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@xpath` | ✅ | XPath to extract links | `"@xpath": ".//a/@href"` |
| `@steps` | ✅ | Steps to execute on followed pages | `"@steps": [...]` |
| `@max-depth` | ❌ | Maximum recursion depth | `"@max-depth": 3` |
| `@detect-cycles` | ❌ | Enable cycle detection | `"@detect-cycles": true` |
| `@follow-external` | ❌ | Follow external domains | `"@follow-external": false` |

### JavaScript Keywords (v0.9+)
| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@javascript` | ✅ | JavaScript code for data extraction | `"@javascript": "return extractData('.item', {...});"` |
| `@code` | ✅ | JavaScript code for actions | `"@code": "window.loadMore();"` |
| `@wait-for` | ❌ | JavaScript condition to wait for | `"@wait-for": "document.querySelectorAll('.item').length > 10"` |
| `@return-json` | ❌ | Parse return value as JSON | `"@return-json": true` |
| `@timeout` | ❌ | Execution timeout (ms) | `"@timeout": 10000` |

### JSON-LD Keywords (v1.0+)
| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@json-ld` | ✅ | JSON-LD extraction configuration | `"@json-ld": {"@schema": "Product"}` |
| `@schema` | ❌ | Filter by schema.org type | `"@schema": "Product"` |
| `@fields` | ❌ | Specific fields to extract | `"@fields": ["name", "price"]` |
| `@all-schemas` | ❌ | Extract all JSON-LD data | `"@all-schemas": true` |

### API Extractor Keywords (v1.0+)
| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@api` | ✅ | API extraction configuration | `"@api": {"@endpoint": "/api/products"}` |
| `@endpoint` | ❌ | API URL pattern (regex) | `"@endpoint": "/api/products/\\d+"` |
| `@method` | ❌ | HTTP method | `"@method": "GET"` |
| `@response-type` | ❌ | Response format | `"@response-type": "json"` |
| `@json-path` | ❌ | JSONPath to extract data | `"@json-path": "$.data.items"` |
| `@fields` | ❌ | Specific fields to extract | `"@fields": ["id", "name"]` |
| `@timeout` | ❌ | Request timeout (ms) | `"@timeout": 10000` |
| `@headers` | ❌ | Custom headers | `"@headers": {"Auth": "Bearer xyz"}` |
| `@params` | ❌ | Query parameters | `"@params": {"limit": 20}` |

## 🚀 JavaScript Execution (NEW)

Execute custom JavaScript code for complex scenarios that require dynamic logic, data manipulation, or advanced browser interactions beyond standard actions:

### JavaScript Actions
Execute JavaScript within the browser action pipeline:

```json5
{
  "@url": "https://dynamic-site.com",
  "@actions": [
    {
      "@type": "javascript",
      "@code": "window.loadMoreContent(); return document.querySelectorAll('.item').length;",
      "@wait-for": "document.querySelectorAll('.item').length > 10",
      "@timeout": 10000
    },
    {
      "@type": "javascript", 
      "@code": "window.scrollTo(0, document.body.scrollHeight); await new Promise(r => setTimeout(r, 2000));"
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='item']",
      "@fields": {
        "title": ".//h3/text()",
        "price": ".//span[@class='price']/text()"
      }
    }
  ]
}
```

### JavaScript Data Extraction
Use JavaScript for complex data extraction that goes beyond XPath capabilities:

```json5
{
  "@url": "https://complex-spa.com/data",
  "@steps": [
    {
      "@javascript": "return Array.from(document.querySelectorAll('.product-card')).map(card => ({ title: card.querySelector('h3').textContent.trim(), price: parseFloat(card.querySelector('.price').textContent.replace('$', '')), inStock: !card.querySelector('.out-of-stock'), rating: card.querySelectorAll('.star.filled').length }));",
      "@name": "products",
      "@return-json": true,
      "@timeout": 5000
    }
  ]
}
```

### Advanced Data Processing
Process and transform data using JavaScript's full capabilities:

```json5
{
  "@url": "https://analytics-dashboard.com",
  "@steps": [
    {
      "@javascript": "const data = Array.from(document.querySelectorAll('.metric')).map(el => ({ name: el.querySelector('.name').textContent, value: parseFloat(el.querySelector('.value').textContent) })); return { metrics: data, total: data.reduce((sum, item) => sum + item.value, 0), average: data.reduce((sum, item) => sum + item.value, 0) / data.length };",
      "@name": "dashboard_summary",
      "@return-json": true
    }
  ]
}
```

### Built-in JavaScript Utilities
DR Web Engine provides common utility functions in all JavaScript execution contexts:

```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@javascript": "return extractData('.product', { title: 'h3', price: '.price', description: '.desc' });",
      "@name": "products"
    }
  ]
}
```

**Available Utility Functions:**
- `extractText(selector)` - Extract text content from elements
- `extractAttribute(selector, attribute)` - Extract attribute values  
- `extractData(selector, fields)` - Extract structured data from elements
- `waitForElements(selector, maxWait)` - Wait for elements to appear
- `scrollAndWait(pixels, waitTime)` - Scroll page and wait

### Dynamic Content Loading
Handle infinite scroll and dynamic content loading:

```json5
{
  "@url": "https://infinite-scroll-site.com",
  "@actions": [
    {
      "@type": "javascript",
      "@code": "let itemCount = 0; while (itemCount < 100) { await scrollAndWait(500, 2000); const newCount = document.querySelectorAll('.item').length; if (newCount === itemCount) break; itemCount = newCount; } return itemCount;",
      "@timeout": 30000
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='item']",
      "@fields": {
        "title": ".//h2/text()",
        "content": ".//p/text()"
      }
    }
  ]
}
```

### Form Manipulation and Complex Interactions
Handle complex form interactions and multi-step processes:

```json5
{
  "@url": "https://complex-form.com",
  "@actions": [
    {
      "@type": "javascript",
      "@code": "const form = document.querySelector('#complex-form'); form.querySelector('select[name=\"category\"]').value = 'electronics'; form.querySelector('input[name=\"price-min\"]').value = '100'; form.querySelector('input[name=\"price-max\"]').value = '500'; form.dispatchEvent(new Event('change', {bubbles: true})); await waitForElements('.filtered-results', 10000);"
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='filtered-results']//div[@class='product']",
      "@fields": {
        "name": ".//h3/text()",
        "price": ".//span[@class='price']/text()"
      }
    }
  ]
}
```

## 📊 JSON-LD Extraction (NEW)

Extract structured data directly from JSON-LD script tags embedded in web pages. Many websites include rich structured data using schema.org vocabulary that can be extracted without complex XPath selectors:

### Extract Product Information
Extract e-commerce product data from structured markup:

```json5
{
  "@url": "https://online-store.com/product/laptop",
  "@steps": [
    {
      "@json-ld": {
        "@schema": "Product",
        "@fields": ["name", "description", "brand", "offers"]
      },
      "@name": "product_data"
    }
  ]
}
```

### Extract Article Metadata
Get article information from news sites and blogs:

```json5
{
  "@url": "https://tech-blog.com/article/ai-trends",
  "@steps": [
    {
      "@json-ld": {
        "@schema": "Article",
        "@fields": ["headline", "author", "datePublished", "articleBody"]
      },
      "@name": "article_info"
    }
  ]
}
```

### Extract Organization Data
Get company information from business websites:

```json5
{
  "@url": "https://company.com/about",
  "@steps": [
    {
      "@json-ld": {
        "@schema": "Organization",
        "@fields": ["name", "address", "contactPoint", "sameAs"]
      },
      "@name": "company_details"
    }
  ]
}
```

### Extract All Structured Data
Capture all JSON-LD data regardless of schema type:

```json5
{
  "@url": "https://restaurant.com",
  "@steps": [
    {
      "@json-ld": {
        "@all-schemas": true
      },
      "@name": "all_structured_data"
    }
  ]
}
```

### Advanced JSON-LD Features

**Schema Type Filtering:**
- Filter by schema.org types (Product, Article, Organization, Event, etc.)
- Handles both simple types and full URLs
- Supports multiple type declarations

**Field Selection:**
- Extract only specific fields you need
- Preserves nested object structure (offers, addresses, etc.)
- Automatic cleaning of JSON-LD metadata

**Graph Structure Support:**
- Handles @graph structures common in complex JSON-LD
- Processes multiple items within single script tags
- Maintains relationships between structured data items

### When to Use JSON-LD vs XPath

**Use JSON-LD when:**
- Site has structured data markup (check page source for `<script type="application/ld+json">`)
- Need clean, semantically correct data
- Want to extract standard e-commerce/article/business data
- Site uses schema.org vocabulary

**Use XPath when:**
- No structured data available
- Need visual/layout-specific extraction
- Custom data not covered by schema.org
- Need to extract from specific page regions

## 🌐 API Extractor (NEW)

Extract data directly from AJAX/REST API calls made by web pages. The API Extractor monitors network requests and captures responses from dynamic content loading.

### Product API Extraction
Extract product data from e-commerce API calls:

```json5
{
  "@url": "https://shop.example.com/products/123",
  "@steps": [
    {
      "@api": {
        "@endpoint": "/api/products/\\d+",  // Regex pattern to match
        "@method": "GET",
        "@response-type": "json",
        "@fields": ["id", "name", "price", "availability", "images"]
      },
      "@name": "product_data"
    }
  ]
}
```

### Search Results API
Extract search results from dynamic loading:

```json5
{
  "@url": "https://search-site.com/results?q=laptops",
  "@steps": [
    {
      "@api": {
        "@endpoint": "/api/search",
        "@response-type": "json",
        "@json-path": "$.data.results",  // Extract specific JSON path
        "@fields": ["title", "price", "rating", "url"]
      },
      "@name": "search_results"
    }
  ]
}
```

### User Profile Data
Extract user data from profile APIs:

```json5
{
  "@url": "https://social-site.com/profile/123",
  "@steps": [
    {
      "@api": {
        "@endpoint": "/api/users/\\d+",
        "@method": "GET",
        "@response-type": "json",
        "@fields": ["username", "bio", "followers", "following"]
      },
      "@name": "profile_data"
    }
  ]
}
```

### Capture All API Calls
Monitor and extract from all API endpoints:

```json5
{
  "@url": "https://dynamic-site.com",
  "@steps": [
    {
      "@api": {
        "@response-type": "json"
        // No endpoint pattern = captures all API calls
      },
      "@name": "all_api_data"
    }
  ]
}
```

### API Extractor Keywords Reference

| Keyword | Purpose | Example |
|---------|---------|---------|
| **@endpoint** | API URL pattern (regex) | `"/api/products/\\d+"` |
| **@method** | HTTP method | `"GET"`, `"POST"`, `"PUT"` |
| **@response-type** | Expected response format | `"json"`, `"text"`, `"xml"` |
| **@json-path** | JSONPath to extract data | `"$.data.items"` |
| **@fields** | Specific fields to extract | `["id", "name", "price"]` |
| **@timeout** | Request timeout (ms) | `10000` |
| **@headers** | Custom request headers | `{"Authorization": "Bearer xyz"}` |
| **@params** | Query parameters | `{"limit": 20, "page": 1}` |

### When to Use API Extractor

**Use API Extractor when:**
- Site loads content dynamically via AJAX
- Data comes from REST/GraphQL APIs
- Need to capture live data updates
- XPath/CSS selectors miss dynamic content
- Site has infinite scroll or lazy loading

**Use other methods when:**
- Content is server-side rendered
- Static HTML extraction is sufficient
- No network requests for target data
- Need specific DOM element targeting

## 🖥️ CLI Reference

```bash
dr-web-engine [OPTIONS]
```

### Required Arguments
- `-q, --query`: Path to query file (JSON5/YAML)
- `-o, --output`: Output file path

### Optional Arguments
| Flag | Description | Default |
|------|-------------|---------|
| `-f, --format` | Query format (`json5`/`yaml`) | `json5` |
| `-l, --log-level` | Log level (`error`/`warning`/`info`/`debug`) | `error` |
| `--log-file` | Path to log file | stdout |
| `--xvfb` | Run in virtual display (headless) | false |

### Examples
```bash
# Basic extraction
dr-web-engine -q query.json5 -o results.json

# With debug logging 
dr-web-engine -q query.json5 -o results.json -l debug

# Headless mode for servers
dr-web-engine -q query.json5 -o results.json --xvfb

# YAML query with log file
dr-web-engine -q query.yaml -o results.json -f yaml --log-file scraping.log

# Multiple runs with timestamp
dr-web-engine -q query.json5 -o "results_$(date +%Y%m%d_%H%M%S).json"
```

### Automation Examples
```bash
# Cron job (daily at 2 AM)
0 2 * * * cd /path/to/queries && dr-web-engine -q daily.json5 -o "data/results_$(date +\%Y\%m\%d).json" --xvfb

# Process multiple queries
for query in queries/*.json5; do
  output="results/$(basename "$query" .json5)_$(date +%Y%m%d).json"
  dr-web-engine -q "$query" -o "$output" --xvfb -l info
done
```

## 🌍 Real-World Examples

### 1. Hacker News with Dynamic Loading
```json5
{
  "@url": "https://news.ycombinator.com",
  "@actions": [
    {"@type": "wait", "@until": "element", "@selector": ".athing", "@timeout": 10000},
    {"@type": "scroll", "@direction": "down", "@pixels": 500}
  ],
  "@steps": [
    {
      "@xpath": "//tr[@class='athing']",
      "@fields": {
        "title": ".//span[@class='titleline']/a/text()",
        "url": ".//span[@class='titleline']/a/@href", 
        "rank": ".//span[@class='rank']/text()"
      }
    }
  ]
}
```

### 2. E-commerce Product Listings
```json5
{
  "@url": "https://example-shop.com/products",
  "@actions": [
    {"@type": "wait", "@until": "network-idle", "@timeout": 10000}
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='product-card']",
      "@fields": {
        "name": ".//h3[@class='product-title']/text()",
        "price": ".//span[@class='price']/text()",
        "image": ".//img/@src",
        "rating": ".//div[@class='rating']/@data-rating",
        "reviews": "normalize-space(.//span[@class='review-count']/text())"
      }
    }
  ],
  "@pagination": {
    "@xpath": "//a[contains(@class, 'next-page')]",
    "@limit": 5
  }
}
```

### 3. Infinite Scroll Social Media
```json5
{
  "@url": "https://social-media-site.com/feed",
  "@actions": [
    {"@type": "wait", "@until": "element", "@selector": ".post"},
    {"@type": "scroll", "@direction": "down", "@pixels": 800},
    {"@type": "wait", "@until": "timeout", "@timeout": 2000},
    {"@type": "scroll", "@direction": "down", "@pixels": 800},
    {"@type": "wait", "@until": "network-idle", "@timeout": 10000}
  ],
  "@steps": [
    {
      "@xpath": "//article[@class='post']",
      "@fields": {
        "content": ".//p[@class='post-text']/text()",
        "author": ".//span[@class='author']/text()",
        "timestamp": ".//time/@datetime",
        "likes": ".//span[@class='like-count']/text()",
        "comments": "count(.//div[@class='comment'])"
      }
    }
  ]
}
```

### 4. Multi-Step Form Interaction
```json5
{
  "@url": "https://job-board.com/search",
  "@actions": [
    {"@type": "fill", "@selector": "input[name='keywords']", "@value": "Python Developer"},
    {"@type": "fill", "@selector": "input[name='location']", "@value": "New York"},
    {"@type": "click", "@selector": "select[name='experience']"},
    {"@type": "click", "@xpath": "//option[text()='3-5 years']"},
    {"@type": "click", "@selector": "button[type='submit']"},
    {"@type": "wait", "@until": "element", "@selector": ".job-listing", "@timeout": 15000}
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='job-listing']",
      "@fields": {
        "title": ".//h3/a/text()",
        "company": ".//span[@class='company']/text()",
        "location": ".//span[@class='location']/text()",
        "salary": ".//span[@class='salary']/text()",
        "url": ".//h3/a/@href"
      }
    }
  ]
}
```

## 🧪 Testing

DR Web Engine has comprehensive test coverage:

```bash
# Run all tests
python -m pytest engine/tests/

# Run specific test categories  
python -m pytest engine/tests/unit/          # Unit tests
python -m pytest engine/tests/integration/   # Integration tests
python -m pytest engine/tests/e2e/          # End-to-end tests

# Run with coverage
python -m pytest engine/tests/ --cov=engine/web_engine --cov-report=html
```

### Test Results
- **70 tests passed, 4 skipped**
- **Unit Tests**: 48 tests (action models, handlers, core functionality)
- **Integration Tests**: 6 tests (engine integration, query execution)
- **E2E Tests**: 6 tests (real-world scenarios - 2 passing, 4 skipped for CI)

### Test Categories
- ✅ **Action Models**: Validation, error handling, type safety
- ✅ **Action Handlers**: Click, scroll, wait, fill, hover functionality  
- ✅ **Action Processor**: Execution pipeline, error handling
- ✅ **Engine Integration**: Query processing, pagination, browser management
- ✅ **Parser Support**: JSON5/YAML query parsing
- ✅ **XPath Extraction**: Field extraction, data transformation

## 📚 Documentation

### Comprehensive Guides
- **[Getting Started Guide](GETTING_STARTED.md)**: Complete tutorial with 20+ examples
- **[Development Roadmap](ROADMAP.md)**: Future features and improvements
- **[API Reference](https://ylli.prifti.us/category/queryable-web/)**: Blog series with advanced patterns

### Quick References
- [Query Keywords](#-query-keywords-reference): Complete keyword reference
- [Action System](#-action-system-new): Browser interaction examples
- [Kleene Star Navigation](#-kleene-star-navigation-new): Recursive link following patterns
- [JavaScript Execution](#-javascript-execution-new): Custom logic and data processing
- [JSON-LD Extraction](#-json-ld-extraction-new): Structured data extraction
- [API Extractor](#-api-extractor-new): Dynamic API data capture
- [CLI Usage](#-cli-reference): Command-line options and automation
- [Real Examples](#-real-world-examples): Production-ready query patterns
- [📚 Examples Directory](examples/): Organized examples by use case

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Clone and setup
git clone https://github.com/starlitlog/dr-web-engine.git
cd dr-web-engine

# Create virtual environment  
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install

# Run tests
python -m pytest engine/tests/
```

### Contribution Areas
- 🐛 **Bug Fixes**: Fix issues and improve reliability
- ✨ **New Actions**: Add new browser interaction types
- 📝 **Documentation**: Improve guides and examples  
- 🧪 **Testing**: Add test coverage and scenarios
- 🚀 **Performance**: Optimize extraction speed
- 🔧 **CLI**: Enhance command-line features

### Submitting Changes
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Commit with clear messages
5. Push and create a Pull Request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 📞 Support

- **📋 Issues**: [GitHub Issues](https://github.com/starlitlog/dr-web-engine/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/starlitlog/dr-web-engine/discussions)
- **📧 Email**: For private inquiries
- **📖 Documentation**: [Getting Started Guide](GETTING_STARTED.md)

## 🏆 Citation

If you use DR Web Engine in research, please cite our paper:

```bibtex
@misc{prifti2025drwebmodernquerybased,
  title         = {Dr Web: a modern, query-based web data retrieval engine},
  author        = {Ylli Prifti and Alessandro Provetti and Pasquale de Meo},
  year          = {2025},
  eprint        = {2504.05311},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DB},
  url           = {https://arxiv.org/abs/2504.05311},
}
```

**[📄 Read the Paper on arXiv →](https://arxiv.org/abs/2504.05311)**

---

<div align="center">

**Made with ❤️ by the DR Web Engine Team**

[⭐ Star on GitHub](https://github.com/starlitlog/dr-web-engine) •
[📦 Install from PyPI](https://pypi.org/project/dr-web-engine/) •
[📖 Read the Docs](GETTING_STARTED.md) •
[🗺️ View Roadmap](ROADMAP.md)

</div>