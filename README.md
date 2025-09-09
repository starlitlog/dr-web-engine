# DR Web Engine

<div align="center">

**Modern, Query-Based Web Data Retrieval Engine**

*Transform any website into a structured data API with simple JSON5/YAML queries*

[![PyPI version](https://badge.fury.io/py/dr-web-engine.svg)](https://badge.fury.io/py/dr-web-engine)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-70%20passed-brightgreen.svg)](#testing)
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
- **⚡ Playwright-Powered**: Reliable automation with modern browser engine
- **🌍 Universal**: Extract from any website - static or JavaScript-heavy SPAs
- **📊 Structured Output**: Get clean JSON data ready for analysis
- **🔧 CLI & Docker**: Run from command line or containerized environments
- **🧪 Thoroughly Tested**: 95+ tests covering all functionality

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation) 
- [Basic Usage](#-basic-usage)
- [Action System](#-action-system-new)
- [Conditional Logic](#-conditional-logic-new)
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
| `@follow` | Follow links | `"@follow": {"@xpath": ".//a/@href"}` |

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
- [CLI Usage](#-cli-reference): Command-line options and automation
- [Real Examples](#-real-world-examples): Production-ready query patterns

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