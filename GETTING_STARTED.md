# Getting Started with DR Web Engine

This guide will teach you how to write queries for DR Web Engine to extract structured data from web pages.

💡 **Quick Start**: Check out our [examples directory](examples/) for ready-to-use patterns organized by use case!

## Query Structure Overview

DR Web Engine uses JSON5 or YAML files to define data extraction queries. Each query contains:

- **Target URL**: The webpage to scrape
- **Steps**: What data to extract and how
- **Optional Features**: Pagination, following links, etc.

## Supported Keywords

### Core Keywords

| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@url` | ✅ | Target webpage URL | `"@url": "https://example.com"` |
| `@steps` | ✅ | Array of extraction steps | `"@steps": [...]` |
| `@xpath` | ✅ | XPath selector for elements | `"@xpath": "//div[@class='item']"` |
| `@fields` | ✅ | Field definitions (name → xpath) | `"@fields": {"title": ".//h2"}` |
| `@name` | ❌ | Name for the extracted data group | `"@name": "products"` |
| `@follow` | ❌ | Follow links for nested extraction | `"@follow": {...}` |
| `@actions` | ❌ | Pre-extraction browser actions | `"@actions": [...]` |
| `@pagination` | ❌ | Configure pagination handling | `"@pagination": {...}` |
| `@limit` | ❌ | Limit pages to process | `"@limit": 5` |

### Action Keywords (NEW in v0.6+)

| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@type` | ✅ | Action type | `"@type": "click"` |
| `@selector` | ❌ | CSS selector for element | `"@selector": "#button"` |
| `@xpath` | ❌ | XPath selector (alternative to @selector) | `"@xpath": "//button[@id='load']"` |
| `@until` | ❌ | Wait condition type | `"@until": "element"` |
| `@timeout` | ❌ | Wait timeout in milliseconds | `"@timeout": 5000` |
| `@direction` | ❌ | Scroll direction | `"@direction": "down"` |
| `@pixels` | ❌ | Scroll distance in pixels | `"@pixels": 500` |
| `@value` | ❌ | Text to fill in form fields | `"@value": "search term"` |
| `@text` | ❌ | Text to wait for | `"@text": "Loading complete"` |

### Conditional Keywords (NEW in v0.7+)

| Keyword | Required | Description | Example |
|---------|----------|-------------|---------|
| `@if` | ✅ | Condition to evaluate | `"@if": {"@exists": "#premium-section"}` |
| `@then` | ✅ | Steps to execute if condition is true | `"@then": [...]` |
| `@else` | ❌ | Steps to execute if condition is false | `"@else": [...]` |
| `@exists` | ❌ | Check if element exists | `"@exists": "#element-id"` |
| `@not-exists` | ❌ | Check if element does not exist | `"@not-exists": ".popup"` |
| `@contains` | ❌ | Check if text contains string | `"@contains": "Premium Content"` |
| `@count` | ❌ | Check exact element count | `"@count": 3` |
| `@min-count` | ❌ | Check minimum element count | `"@min-count": 1` |
| `@max-count` | ❌ | Check maximum element count | `"@max-count": 10` |

## Basic Query Examples

### Simple Extraction (JSON5)

```json5
{
  "@url": "https://example.com/products",
  "@steps": [
    {
      "@xpath": "//div[@class='product']",
      "@name": "products",
      "@fields": {
        "title": ".//h2/text()",
        "price": ".//span[@class='price']/text()",
        "image": ".//img/@src"
      }
    }
  ]
}
```

### Simple Extraction (YAML)

```yaml
url: https://example.com/products
steps:
  - xpath: //div[@class='product']
    name: products
    fields:
      title: .//h2/text()
      price: .//span[@class='price']/text()
      image: .//img/@src
```

## Browser Actions (NEW in v0.6+)

The Action System enables interaction with dynamic web pages before data extraction. Perfect for modern JavaScript-heavy sites.

### Supported Action Types

**Click Actions** - Click buttons, links, or any element:
```json5
{"@type": "click", "@selector": "#load-more-btn"}
{"@type": "click", "@xpath": "//button[text()='Show More']"}
```

**Scroll Actions** - Scroll to trigger infinite loading or reveal content:
```json5
{"@type": "scroll", "@direction": "down", "@pixels": 500}
{"@type": "scroll", "@selector": "#content-bottom"}  // Scroll to element
```

**Wait Actions** - Wait for dynamic content to load:
```json5
{"@type": "wait", "@until": "element", "@selector": ".loaded", "@timeout": 10000}
{"@type": "wait", "@until": "text", "@selector": "#status", "@text": "Complete"}
{"@type": "wait", "@until": "network-idle", "@timeout": 5000}
{"@type": "wait", "@until": "timeout", "@timeout": 3000}  // Simple delay
```

**Fill Actions** - Fill form fields:
```json5
{"@type": "fill", "@selector": "input[name='search']", "@value": "query text"}
{"@type": "fill", "@xpath": "//input[@placeholder='Search']", "@value": "keywords"}
```

**Hover Actions** - Trigger hover effects:
```json5
{"@type": "hover", "@selector": ".dropdown-trigger"}
{"@type": "hover", "@xpath": "//div[@class='menu-item']"}
```

### Action Examples

#### JavaScript-Rendered Content
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

#### Infinite Scroll Loading
```json5
{
  "@url": "https://infinite-scroll-site.com",
  "@actions": [
    {"@type": "wait", "@until": "element", "@selector": ".item"},
    {"@type": "scroll", "@direction": "down", "@pixels": 800},
    {"@type": "wait", "@until": "timeout", "@timeout": 2000},
    {"@type": "scroll", "@direction": "down", "@pixels": 800}, 
    {"@type": "wait", "@until": "timeout", "@timeout": 2000},
    {"@type": "scroll", "@direction": "down", "@pixels": 800},
    {"@type": "wait", "@until": "network-idle", "@timeout": 10000}
  ],
  "@steps": [
    {
      "@xpath": "//article[@class='item']",
      "@fields": {
        "title": ".//h2/text()",
        "content": ".//p/text()"
      }
    }
  ]
}
```

#### Search Form Interaction
```json5
{
  "@url": "https://example-search.com",
  "@actions": [
    {
      "@type": "fill",
      "@selector": "input[name='q']",
      "@value": "dr web engine"
    },
    {
      "@type": "click", 
      "@selector": "button[type='submit']"
    },
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".search-results"
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='result']",
      "@fields": {
        "title": ".//h3/text()",
        "url": ".//a/@href",
        "description": ".//p/text()"
      }
    }
  ]
}
```

## Conditional Logic (NEW in v0.7+)

The Conditional System enables dynamic branching logic in your extraction queries. Extract different data based on page conditions like element presence, text content, or element counts.

### Supported Condition Types

**Element Existence** - Check if elements exist on the page:
```json5
{"@exists": "#premium-section"}         // Element exists
{"@not-exists": ".advertisement"}       // Element does not exist
{"@exists": "//div[@class='premium']"}  // XPath support
```

**Text Content** - Check for specific text:
```json5
{"@contains": "Premium Content"}                              // Page contains text
{"@contains": "VIP", "@selector": ".user-badge"}            // Element contains text
{"@contains": "Error", "@xpath": "//div[@class='status']"}  // XPath text check
```

**Element Count** - Check number of elements:
```json5
{"@count": 5, "@selector": ".item"}           // Exactly 5 items
{"@min-count": 1, "@selector": ".result"}     // At least 1 result
{"@max-count": 10, "@xpath": "//article"}     // At most 10 articles
```

### Basic Conditional Examples

#### Premium vs Free Content Detection
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

#### User Authentication State Detection
```json5
{
  "@url": "https://forum.example.com",
  "@steps": [
    {
      "@if": {"@exists": ".user-menu"},
      "@then": [
        {
          "@xpath": "//div[@class='post authenticated']",
          "@fields": {
            "author": ".//span[@class='username']/text()",
            "content": ".//div[@class='post-body']/text()",
            "edit_link": ".//a[@class='edit']/@href",
            "vote_score": ".//span[@class='score']/text()"
          }
        }
      ],
      "@else": [
        {
          "@xpath": "//div[@class='post guest']",
          "@fields": {
            "author": ".//span[@class='username']/text()",
            "content": ".//div[@class='post-preview']/text()",
            "login_prompt": ".//div[@class='login-required']/text()"
          }
        }
      ]
    }
  ]
}
```

#### Search Results Count Handling
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
            "snippet": ".//p[@class='description']/text()",
            "rank": "position()"
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

### Advanced Conditional Examples

#### Nested Conditionals for Complex Logic
```json5
{
  "@url": "https://ecommerce-site.com/product/123",
  "@steps": [
    {
      "@if": {"@exists": "#product-page"},
      "@then": [
        {
          "@if": {"@contains": "In Stock", "@selector": ".availability"},
          "@then": [
            {
              "@xpath": "//div[@class='product available']",
              "@fields": {
                "name": ".//h1/text()",
                "price": ".//span[@class='price']/text()",
                "stock_count": ".//span[@class='stock']/text()",
                "add_to_cart": ".//button[@class='add-cart']/@data-product-id"
              }
            }
          ],
          "@else": [
            {
              "@if": {"@contains": "Pre-order", "@selector": ".availability"},
              "@then": [
                {
                  "@xpath": "//div[@class='product preorder']",
                  "@fields": {
                    "name": ".//h1/text()",
                    "price": ".//span[@class='price']/text()",
                    "release_date": ".//span[@class='release']/text()",
                    "preorder_button": ".//button[@class='preorder']/@data-product-id"
                  }
                }
              ],
              "@else": [
                {
                  "@xpath": "//div[@class='product unavailable']",
                  "@fields": {
                    "name": ".//h1/text()",
                    "unavailable_message": ".//div[@class='out-of-stock']/text()",
                    "notify_button": ".//button[@class='notify']/@data-product-id"
                  }
                }
              ]
            }
          ]
        }
      ],
      "@else": [
        {
          "@xpath": "//div[@class='error-page']",
          "@fields": {
            "error_message": ".//text()",
            "error_code": "./@data-error"
          }
        }
      ]
    }
  ]
}
```

#### Combining Actions with Conditionals
```json5
{
  "@url": "https://dynamic-site.com",
  "@actions": [
    {"@type": "wait", "@until": "element", "@selector": "#content"},
    {"@type": "click", "@selector": "#load-more"}
  ],
  "@steps": [
    {
      "@if": {"@contains": "Premium", "@selector": ".user-status"},
      "@then": [
        {
          "@xpath": "//article[@class='premium-content']",
          "@fields": {
            "title": ".//h2/text()",
            "full_text": ".//div[@class='content']/text()",
            "premium_media": ".//video/@src"
          }
        }
      ],
      "@else": [
        {
          "@if": {"@max-count": 0, "@selector": ".paywall"},
          "@then": [
            {
              "@xpath": "//article[@class='free-content']",
              "@fields": {
                "title": ".//h2/text()",
                "preview": ".//div[@class='preview']/text()"
              }
            }
          ],
          "@else": [
            {
              "@xpath": "//div[@class='paywall-message']",
              "@fields": {
                "title": ".//h2/text()",
                "subscription_offer": ".//div[@class='offer']/text()",
                "price": ".//span[@class='price']/text()"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

#### Multi-Language Content Detection
```json5
{
  "@url": "https://international-news.com/article/456",
  "@steps": [
    {
      "@if": {"@contains": "English", "@selector": "html[lang]"},
      "@then": [
        {
          "@xpath": "//article[@lang='en']",
          "@fields": {
            "headline": ".//h1/text()",
            "content": ".//div[@class='article-body']/p/text()",
            "author": ".//span[@class='byline']/text()",
            "language": "'English'"
          }
        }
      ],
      "@else": [
        {
          "@if": {"@contains": "Español", "@selector": "html[lang]"},
          "@then": [
            {
              "@xpath": "//article[@lang='es']",
              "@fields": {
                "titular": ".//h1/text()",
                "contenido": ".//div[@class='article-body']/p/text()",
                "autor": ".//span[@class='byline']/text()",
                "idioma": "'Español'"
              }
            }
          ],
          "@else": [
            {
              "@xpath": "//article",
              "@fields": {
                "title": ".//h1/text()",
                "content": ".//div[@class='article-body']/p/text()",
                "detected_lang": "./@lang | ./ancestor::html/@lang"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Conditional Logic with Following Links

#### Adaptive Content Extraction Based on Page Type
```json5
{
  "@url": "https://blog-aggregator.com",
  "@steps": [
    {
      "@xpath": "//article[@class='post-preview']",
      "@fields": {
        "title": ".//h2/a/text()",
        "excerpt": ".//div[@class='excerpt']/text()"
      },
      "@follow": {
        "@xpath": ".//h2/a/@href",
        "@steps": [
          {
            "@if": {"@exists": ".video-player"},
            "@then": [
              {
                "@xpath": "//div[@class='video-post']",
                "@fields": {
                  "type": "'video'",
                  "title": ".//h1/text()",
                  "video_url": ".//video/@src",
                  "duration": ".//span[@class='duration']/text()",
                  "transcript": ".//div[@class='transcript']/text()"
                }
              }
            ],
            "@else": [
              {
                "@if": {"@exists": ".image-gallery"},
                "@then": [
                  {
                    "@xpath": "//div[@class='gallery-post']",
                    "@fields": {
                      "type": "'gallery'",
                      "title": ".//h1/text()",
                      "images": ".//img/@src",
                      "captions": ".//figcaption/text()"
                    }
                  }
                ],
                "@else": [
                  {
                    "@xpath": "//article[@class='text-post']",
                    "@fields": {
                      "type": "'text'",
                      "title": ".//h1/text()",
                      "content": ".//div[@class='post-content']/p/text()",
                      "word_count": "string-length(.//div[@class='post-content'])"
                    }
                  }
                ]
              }
            ]
          }
        ]
      }
    }
  ]
}
```

### Conditional Best Practices

#### 1. Element Existence Checks
```json5
// Good: Specific selectors
{"@exists": "#premium-badge"}
{"@exists": ".user-authenticated"}

// Better: Content-based checks
{"@exists": "//div[contains(@class, 'premium') and contains(text(), 'VIP')]"}
```

#### 2. Text Content Matching
```json5
// Good: Direct text matching
{"@contains": "Premium Content"}

// Better: Case-insensitive matching with XPath
{"@contains": "premium", "@selector": "*[contains(translate(text(), 'PREMIUM', 'premium'), 'premium')]"}
```

#### 3. Robust Count Checks
```json5
// Handle edge cases
{
  "@if": {"@min-count": 1, "@selector": ".search-result"},
  "@then": [
    {
      "@if": {"@max-count": 50, "@selector": ".search-result"},
      "@then": [
        // Normal result extraction
      ],
      "@else": [
        // Handle too many results case
      ]
    }
  ],
  "@else": [
    // Handle no results case
  ]
}
```

#### 4. Fallback Strategies
Always provide `@else` branches for robust scraping:
```json5
{
  "@if": {"@exists": "#new-layout"},
  "@then": [
    // Extract using new layout selectors
  ],
  "@else": [
    // Fallback to old layout selectors
  ]
}
```

#### 5. Performance Considerations
- Use specific selectors to minimize DOM traversal
- Prefer CSS selectors over complex XPath when possible
- Avoid deep nesting of conditionals when not necessary

### Error Handling in Conditionals

Conditions gracefully handle errors:
- Missing elements return `false` for `@exists`
- Text checks on missing elements return `false`
- Count checks on missing elements return `0`
- Failed conditions execute `@else` branch or skip if no `@else`

### Conditional Logic Examples in YAML

```yaml
url: https://example.com/content
steps:
  - if:
      exists: "#premium-section" 
    then:
      - xpath: //div[@class='premium-content']
        fields:
          title: .//h1/text()
          content: .//div[@class='full-text']/text()
    else:
      - xpath: //div[@class='free-content']
        fields:
          title: .//h1/text()
          preview: .//div[@class='preview']/text()
```

## Advanced Features

### Following Links (@follow)

Extract data from linked pages by using the `@follow` keyword:

```json5
{
  "@url": "https://example.com/articles",
  "@steps": [
    {
      "@xpath": "//article",
      "@fields": {
        "title": ".//h2/text()",
        "summary": ".//p[@class='summary']/text()"
      },
      "@follow": {
        "@xpath": ".//a[@class='read-more']/@href",
        "@steps": [
          {
            "@xpath": "//article[@class='full-article']",
            "@name": "full_content",
            "@fields": {
              "content": ".//div[@class='content']/text()",
              "author": ".//span[@class='author']/text()",
              "publish_date": ".//time/@datetime"
            }
          }
        ]
      }
    }
  ]
}
```

### Pagination (@pagination)

Handle multi-page results:

```json5
{
  "@url": "https://example.com/search?q=query",
  "@steps": [
    {
      "@xpath": "//div[@class='result']",
      "@fields": {
        "title": ".//h3/text()",
        "link": ".//a/@href"
      }
    }
  ],
  "@pagination": {
    "@xpath": "//a[@class='next-page']/@href",
    "@limit": 10
  }
}
```

## XPath Guide for DR Web Engine

### Basic Selectors

```xpath
//div                    # All div elements
//div[@class='item']     # Divs with class 'item'
//div[@id='content']     # Div with id 'content'
//a[@href]              # All links with href attribute
```

### Text and Attributes

```xpath
.//h2/text()           # Text content of h2 (relative to current element)
.//img/@src            # src attribute of img (relative to current element)
.//a/@href             # href attribute of link
.//span[@class='price']/normalize-space()  # Normalized text content
```

### Advanced Selectors

```xpath
//div[contains(@class, 'product')]     # Divs containing 'product' in class
//span[text()='Price:']/following::text()  # Text following a specific element
//div[position()=1]                    # First div element
//a[starts-with(@href, 'https://')]    # Links starting with https://
```

## Complete Examples

### E-commerce Product Scraping

```json5
{
  "@url": "https://shop.example.com/category/electronics",
  "@steps": [
    {
      "@xpath": "//div[@class='product-card']",
      "@name": "products",
      "@fields": {
        "name": ".//h3[@class='product-title']/text()",
        "price": ".//span[@class='price']/text()",
        "rating": ".//div[@class='rating']/@data-rating",
        "image": ".//img[@class='product-image']/@src",
        "availability": ".//span[@class='stock-status']/text()"
      },
      "@follow": {
        "@xpath": ".//a[@class='product-link']/@href",
        "@steps": [
          {
            "@xpath": "//div[@class='product-details']",
            "@name": "details",
            "@fields": {
              "description": ".//div[@class='description']/text()",
              "specifications": ".//div[@class='specs']/text()",
              "reviews_count": ".//span[@class='review-count']/text()"
            }
          },
          {
            "@xpath": "//div[@class='review']",
            "@name": "reviews",
            "@fields": {
              "reviewer": ".//span[@class='reviewer-name']/text()",
              "rating": ".//div[@class='review-rating']/@data-rating",
              "comment": ".//p[@class='review-text']/text()",
              "date": ".//time/@datetime"
            }
          }
        ]
      }
    }
  ],
  "@pagination": {
    "@xpath": "//a[@class='next-page']/@href",
    "@limit": 5
  }
}
```

### News Articles with Comments

```yaml
url: https://news.example.com/technology
steps:
  - xpath: //article[@class='news-item']
    fields:
      headline: .//h2[@class='headline']/text()
      summary: .//p[@class='summary']/text()
      author: .//span[@class='author']/text()
      publish_time: .//time/@datetime
      category: .//span[@class='category']/text()
    follow:
      xpath: .//a[@class='read-more']/@href
      steps:
        - xpath: //article[@class='full-article']
          name: article_content
          fields:
            full_text: .//div[@class='article-body']/text()
            tags: .//span[@class='tag']/text()
            shares: .//span[@class='share-count']/text()
        - xpath: //div[@class='comment']
          name: comments
          fields:
            commenter: .//span[@class='commenter']/text()
            comment_text: .//p[@class='comment-body']/text()
            comment_time: .//time/@datetime
            upvotes: .//span[@class='upvotes']/text()
pagination:
  xpath: //a[@id='next-page']/@href
  limit: 3
```

## Command Line Interface (CLI)

### Basic Usage

To execute queries using the CLI:
```bash
dr-web-engine -q your_query.json5 -o results.json
```

### Complete CLI Options

| Option | Short | Required | Description | Default | Example |
|--------|-------|----------|-------------|---------|---------|
| `--query` | `-q` | ✅ | Path to query file (JSON5/YAML) | - | `-q scraper.json5` |
| `--output` | `-o` | ✅ | Output file for results | - | `-o results.json` |
| `--format` | `-f` | ❌ | Query format (`json5` or `yaml`) | `json5` | `-f yaml` |
| `--log-level` | `-l` | ❌ | Logging level | `error` | `-l debug` |
| `--log-file` | - | ❌ | Save logs to file | stdout | `--log-file scraping.log` |
| `--xvfb` | - | ❌ | Headless mode with Xvfb | `false` | `--xvfb` |
| `--help` | - | ❌ | Show help message | - | `--help` |

### Logging Levels

- `error` - Only show critical errors
- `warning` - Show warnings and errors  
- `info` - Show general information + warnings/errors
- `debug` - Show detailed debugging information (recommended for development)

### Usage Examples

```bash
# Basic scraping
dr-web-engine -q hacker_news.json5 -o results.json

# With debug logging
dr-web-engine -q complex_query.json5 -o results.json -l debug

# Save logs to file
dr-web-engine -q query.yaml -o results.json -f yaml --log-file scraping.log

# Headless mode (useful for servers/automation)
dr-web-engine -q query.json5 -o results.json --xvfb -l info

# Full verbose example
dr-web-engine \
  --query ./queries/github_trending.json5 \
  --output ./results/$(date +%Y%m%d)_github_results.json \
  --format json5 \
  --log-level info \
  --log-file ./logs/scraping_$(date +%Y%m%d).log \
  --xvfb
```

## Automation and Scheduling

### Cron Job Setup

#### 1. Basic Scheduled Scraping

Create a cron job for daily scraping at 2 AM:

```bash
# Edit crontab
crontab -e

# Add this line for daily execution at 2:00 AM
0 2 * * * /usr/local/bin/dr-web-engine -q /path/to/queries/daily_scrape.json5 -o /path/to/results/$(date +\%Y\%m\%d)_results.json --xvfb --log-file /path/to/logs/scraping_$(date +\%Y\%m\%d).log
```

#### 2. Advanced Automation Script

Create a wrapper script for more complex automation:

**scrape_automation.sh:**
```bash
#!/bin/bash

# Configuration
QUERY_DIR="/home/user/scraping/queries"
RESULTS_DIR="/home/user/scraping/results" 
LOGS_DIR="/home/user/scraping/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create directories if they don't exist
mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

# Function to run scraping with error handling
run_scrape() {
    local query_file="$1"
    local name="$2"
    
    echo "Starting scrape: $name at $(date)"
    
    dr-web-engine \
        -q "$QUERY_DIR/$query_file" \
        -o "$RESULTS_DIR/${TIMESTAMP}_${name}.json" \
        --xvfb \
        -l info \
        --log-file "$LOGS_DIR/${TIMESTAMP}_${name}.log"
    
    if [ $? -eq 0 ]; then
        echo "✅ $name completed successfully"
    else
        echo "❌ $name failed - check logs"
        # Send notification (optional)
        # mail -s "Scraping Failed: $name" admin@example.com < "$LOGS_DIR/${TIMESTAMP}_${name}.log"
    fi
}

# Run multiple scrapers
run_scrape "hacker_news.json5" "hackernews"
run_scrape "github_trending.json5" "github"
run_scrape "lobsters.json5" "lobsters"

# Cleanup old files (keep last 30 days)
find "$RESULTS_DIR" -name "*.json" -mtime +30 -delete
find "$LOGS_DIR" -name "*.log" -mtime +30 -delete

echo "All scraping tasks completed at $(date)"
```

Make it executable and add to cron:
```bash
chmod +x scrape_automation.sh

# Add to crontab for daily execution
0 2 * * * /path/to/scrape_automation.sh >> /path/to/logs/cron.log 2>&1
```

#### 3. Multiple Schedule Examples

```bash
# Every hour during business hours (9 AM - 5 PM, Mon-Fri)
0 9-17 * * 1-5 /usr/local/bin/dr-web-engine -q /path/to/hourly_query.json5 -o /path/to/results/hourly_$(date +\%Y\%m\%d_\%H\%M).json --xvfb

# Every 30 minutes
*/30 * * * * /path/to/scrape_automation.sh

# Weekly on Sunday at 3 AM
0 3 * * 0 /usr/local/bin/dr-web-engine -q /path/to/weekly_deep_scrape.json5 -o /path/to/results/weekly_$(date +\%Y_week\%U).json --xvfb

# Monthly on the 1st at midnight
0 0 1 * * /path/to/monthly_scrape.sh
```

### Adding Timestamps to Output

#### Method 1: Modify Output with Timestamps

Create a post-processing script **add_metadata.py**:

```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime
import os

def add_extraction_metadata(input_file, output_file):
    """Add extraction metadata to JSON results"""
    
    # Read the original results
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Add metadata
    metadata = {
        "extraction_info": {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "unix_timestamp": int(datetime.now().timestamp()),
            "timezone": datetime.now().astimezone().tzname(),
            "scraper_version": "dr-web-engine-0.5.6b",
            "total_records": len(data) if isinstance(data, list) else 1
        }
    }
    
    # Combine metadata with results
    if isinstance(data, dict):
        data["_metadata"] = metadata
    elif isinstance(data, list):
        final_data = {
            "_metadata": metadata,
            "results": data
        }
        data = final_data
    
    # Write enhanced results
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_metadata.py input.json output.json")
        sys.exit(1)
    
    add_extraction_metadata(sys.argv[1], sys.argv[2])
```

#### Method 2: Enhanced Automation Script with Metadata

**enhanced_scraper.sh:**
```bash
#!/bin/bash

QUERY_FILE="$1"
OUTPUT_BASE="$2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEMP_OUTPUT="/tmp/scraping_temp_${TIMESTAMP}.json"
FINAL_OUTPUT="${OUTPUT_BASE}_${TIMESTAMP}.json"

# Run the scraping
dr-web-engine \
    -q "$QUERY_FILE" \
    -o "$TEMP_OUTPUT" \
    --xvfb \
    -l info \
    --log-file "${OUTPUT_BASE}_${TIMESTAMP}.log"

# Add metadata
python3 add_metadata.py "$TEMP_OUTPUT" "$FINAL_OUTPUT"

# Cleanup temp file
rm "$TEMP_OUTPUT"

echo "Results with metadata saved to: $FINAL_OUTPUT"
```

Usage:
```bash
./enhanced_scraper.sh queries/hackernews.json5 results/hackernews
```

#### Method 3: Timestamped File Naming

```bash
# Various timestamp formats for file naming
DATE=$(date +%Y-%m-%d)
DATETIME=$(date +%Y%m%d_%H%M%S)
ISO_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Examples
dr-web-engine -q query.json5 -o "results_${DATE}.json"
dr-web-engine -q query.json5 -o "scrape_${DATETIME}.json"
dr-web-engine -q query.json5 -o "data_$(date +%Y_week%U).json"  # Weekly
```

### Monitoring and Alerting

#### Log Monitoring Script

**monitor_scraping.sh:**
```bash
#!/bin/bash

LOG_DIR="/path/to/logs"
ALERT_EMAIL="admin@example.com"

# Check for recent errors
RECENT_ERRORS=$(find "$LOG_DIR" -name "*.log" -mtime -1 -exec grep -l "ERROR" {} \;)

if [ -n "$RECENT_ERRORS" ]; then
    echo "Scraping errors detected in the last 24 hours:"
    echo "$RECENT_ERRORS"
    # Send alert email
    echo "Recent scraping errors detected. Check logs: $RECENT_ERRORS" | \
        mail -s "DR Web Engine Alert" "$ALERT_EMAIL"
fi
```

### Best Practices for Automation

1. **Resource Management**
   - Use `--xvfb` for headless operation
   - Set appropriate log levels (`info` for production)
   - Implement log rotation

2. **Error Handling** 
   - Always check exit codes
   - Implement retry logic for failed scrapes
   - Set up monitoring and alerting

3. **Storage Management**
   - Use timestamped filenames
   - Implement cleanup of old files
   - Consider compression for long-term storage

4. **Rate Limiting**
   - Add delays between scraping different sites
   - Respect robots.txt and terms of service
   - Monitor for IP blocking

5. **Security**
   - Store queries and scripts in version control
   - Use environment variables for sensitive data
   - Set appropriate file permissions

## Tips and Best Practices

### 1. Start Simple
Begin with a basic query targeting one element type, then gradually add complexity.

### 2. Test XPath Selectors
Use browser developer tools to test your XPath expressions before adding them to queries.

### 3. Handle Dynamic Content
For JavaScript-heavy sites, ensure elements are loaded before extraction. DR Web Engine uses Playwright which handles most dynamic content automatically.

### 4. Use Relative XPath
In `@fields`, use relative XPath (starting with `./`) to search within the current element context.

### 5. Extract Attributes
For links, images, and other elements with important attributes, use `@attribute` syntax:
```xpath
.//img/@src      # Get image source
.//a/@href       # Get link URL
.//div/@data-id  # Get data attribute
```

### 6. Handle Text Properly
Use `text()` for direct text content or `normalize-space()` for cleaned text:
```xpath
.//span/text()                    # Direct text
.//span/normalize-space()         # Trimmed text
```

### 7. Pagination Limits
Always set reasonable `@limit` values for pagination to avoid infinite loops.

### 8. Error Handling
The engine will log warnings for missing elements but continue processing. Check logs for debugging.

## Troubleshooting

### Common Issues

1. **No data extracted**: Check if your XPath selectors match the actual HTML structure
2. **Partial data**: Verify that all field XPath expressions are relative to the step XPath
3. **Pagination not working**: Ensure the pagination XPath points to the actual next page link
4. **Follow links failing**: Check that the follow XPath returns valid URLs

### Debugging Tips

1. Use `debug` log level to see detailed extraction information
2. Test XPath selectors in browser developer tools
3. Start with simple queries and add complexity gradually
4. Verify the target website structure hasn't changed

## Real-World Progressive Examples

The following examples demonstrate scraping three challenging websites from different domains, progressing from simple to complex queries.

### 1. News Domain: Hacker News

#### Level 1: Simple Story Listing

Extract basic story information from Hacker News front page:

```json5
{
  "@url": "https://news.ycombinator.com",
  "@steps": [
    {
      "@xpath": "//tr[@class='athing']",
      "@name": "stories",
      "@fields": {
        "id": "./@id",
        "rank": ".//span[@class='rank']/text()",
        "title": ".//span[@class='titleline']/a/text()",
        "url": ".//span[@class='titleline']/a/@href",
        "domain": ".//span[@class='sitestr']/text()"
      }
    }
  ]
}
```

#### Level 2: Story with Metadata and Actions

Add scores, authors, timestamps, and handle dynamic loading:

```json5
{
  "@url": "https://news.ycombinator.com",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".athing",
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
      "@xpath": "//tr[@class='athing']",
      "@name": "stories",
      "@fields": {
        "id": "./@id",
        "title": ".//span[@class='titleline']/a/text()",
        "url": ".//span[@class='titleline']/a/@href",
        "domain": ".//span[@class='sitestr']/text()",
        "score": "./following-sibling::tr//span[@class='score']/text()",
        "author": "./following-sibling::tr//a[@class='hnuser']/text()",
        "time": "./following-sibling::tr//span[@class='age']/@title",
        "comments": "./following-sibling::tr//a[contains(@href, 'item?id=')]/text()"
      }
    }
  ]
}
```

#### Level 3: Following to Comments

Extract story details and comments:

```json5
{
  "@url": "https://news.ycombinator.com",
  "@steps": [
    {
      "@xpath": "//tr[@class='athing']",
      "@name": "stories",
      "@fields": {
        "title": ".//span[@class='titleline']/a/text()",
        "url": ".//span[@class='titleline']/a/@href"
      },
      "@follow": {
        "@xpath": "./following-sibling::tr//a[contains(@href, 'item?id=')]/@href",
        "@steps": [
          {
            "@xpath": "//tr[@class='athing comtr']",
            "@name": "comments",
            "@fields": {
              "author": ".//a[@class='hnuser']/text()",
              "time": ".//span[@class='age']/@title",
              "text": ".//div[@class='commtext']//text()",
              "indent": ".//img[@class='s']/@width"
            }
          }
        ]
      }
    }
  ]
}
```

### 2. Social Domain: GitHub Trending

Since Reddit blocks scraping, we'll use GitHub Trending as our social example:

#### Level 1: Basic Repository List

```json5
{
  "@url": "https://github.com/trending",
  "@steps": [
    {
      "@xpath": "//article[@class='Box-row']",
      "@name": "repositories",
      "@fields": {
        "name": ".//h2[@class='h3 lh-condensed']//a/@href",
        "title": ".//h2[@class='h3 lh-condensed']//a/text()",
        "description": ".//p[@class='col-9 color-fg-muted my-1 pr-4']/text()",
        "language": ".//span[@itemprop='programmingLanguage']/text()",
        "stars": ".//a[contains(@href, '/stargazers')]/text()"
      }
    }
  ]
}
```

#### Level 2: Repository with Full Metadata and Dynamic Loading

```json5
{
  "@url": "https://github.com/trending",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@selector": "article.Box-row",
      "@timeout": 10000
    },
    {
      "@type": "scroll",
      "@direction": "down",
      "@pixels": 800
    },
    {
      "@type": "wait",
      "@until": "network-idle",
      "@timeout": 5000
    }
  ],
  "@steps": [
    {
      "@xpath": "//article[@class='Box-row']",
      "@name": "repositories",
      "@fields": {
        "full_name": ".//h2[@class='h3 lh-condensed']//a/@href",
        "title": ".//h2[@class='h3 lh-condensed']//a/text()",
        "description": ".//p[@class='col-9 color-fg-muted my-1 pr-4']/text()",
        "language": ".//span[@itemprop='programmingLanguage']/text()",
        "total_stars": ".//a[contains(@href, '/stargazers')]/text()",
        "forks": ".//a[contains(@href, '/forks')]/text()",
        "stars_today": ".//span[@class='d-inline-block float-sm-right']/text()",
        "built_by": ".//img[@class='avatar mb-1']/@alt"
      }
    }
  ]
}
```

#### Level 3: Following to Repository Details

```json5
{
  "@url": "https://github.com/trending",
  "@steps": [
    {
      "@xpath": "//article[@class='Box-row']",
      "@name": "repositories",
      "@fields": {
        "name": ".//h2[@class='h3 lh-condensed']//a/text()",
        "url": ".//h2[@class='h3 lh-condensed']//a/@href"
      },
      "@follow": {
        "@xpath": ".//h2[@class='h3 lh-condensed']//a/@href",
        "@steps": [
          {
            "@xpath": "//div[@id='repository-container-header']",
            "@name": "repo_details",
            "@fields": {
              "full_description": ".//p[@class='f4 my-3']/text()",
              "website": ".//a[@data-testid='home-link']/@href",
              "topics": ".//a[@class='topic-tag topic-tag-link']/text()",
              "license": ".//a[contains(@href, '/blob/main/LICENSE')]/text()"
            }
          },
          {
            "@xpath": "//div[@class='Box-row Box-row--focus-gray py-2']",
            "@name": "recent_commits",
            "@fields": {
              "message": ".//a[@class='Link--primary text-bold js-navigation-open markdown-title']/text()",
              "author": ".//a[@class='commit-author user-mention']/text()",
              "date": ".//relative-time/@datetime",
              "sha": ".//a[@class='f6 Link--secondary text-mono ml-2']/@href"
            }
          }
        ]
      }
    }
  ]
}
```

### 3. International News: Libero Quotidiano (Anti-Scraping)

**Challenge Level: Hard** - Italian newspaper with active anti-scraping measures

This example demonstrates handling a real-world challenging website that actively works against scraping. Libero Quotidiano uses Next.js with dynamic content loading and JavaScript-heavy rendering.

#### Level 1: Basic Article Listing

Extract all article titles and links from the homepage:

```json5
{
  "@url": "https://www.liberoquotidiano.it/",
  "@steps": [
    {
      "@xpath": "//a[contains(@href, '/news/') and normalize-space(text())]",
      "@name": "articles",
      "@fields": {
        "title": "./text()",
        "url": "./@href",
        "category": "substring-before(substring-after(./@href, '/news/'), '/')"
      }
    }
  ]
}
```

#### Level 2: Filter Articles with Dynamic Loading

Extract only articles containing "Giorgia" in the title, handling JavaScript rendering:

```json5
{
  "@url": "https://www.liberoquotidiano.it/",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@xpath": "//a[contains(@href, '/news/')]",
      "@timeout": 15000
    },
    {
      "@type": "scroll",
      "@direction": "down",
      "@pixels": 1000
    },
    {
      "@type": "wait",
      "@until": "timeout",
      "@timeout": 3000
    },
    {
      "@type": "wait",
      "@until": "network-idle",
      "@timeout": 10000
    }
  ],
  "@steps": [
    {
      "@xpath": "//a[contains(@href, '/news/') and contains(normalize-space(text()), 'Giorgia')]",
      "@name": "giorgia_articles",
      "@fields": {
        "title": "./text()",
        "url": "./@href"
      }
    }
  ]
}
```

#### Level 3: Following to Full Article Content

Extract complete article content by following links:

```json5
{
  "@url": "https://www.liberoquotidiano.it/",
  "@steps": [
    {
      "@xpath": "//a[contains(@href, '/news/') and contains(normalize-space(text()), 'Giorgia')]",
      "@name": "giorgia_articles",
      "@fields": {
        "title": "./text()",
        "url": "./@href",
        "category": "substring-before(substring-after(./@href, '/news/'), '/')"
      },
      "@follow": {
        "@xpath": "./@href",
        "@steps": [
          {
            "@xpath": "//article | //div[contains(@class, 'content')] | //div[contains(@class, 'article')]",
            "@name": "article_content",
            "@fields": {
              "headline": ".//h1/text() | .//h2/text()",
              "subtitle": ".//h3/text() | .//p[@class='subtitle']/text()",
              "content": ".//p[not(@class) or @class='']//text()",
              "author": ".//span[contains(@class, 'author')]/text() | .//div[contains(@class, 'byline')]//text()",
              "publish_date": ".//time/@datetime | .//span[contains(@class, 'date')]/text()",
              "tags": ".//span[contains(@class, 'tag')]//text()"
            }
          },
          {
            "@xpath": "//div[contains(@class, 'related')] | //div[contains(@class, 'correlati')]",
            "@name": "related_articles",
            "@fields": {
              "title": ".//a/text()",
              "url": ".//a/@href"
            }
          }
        ]
      }
    }
  ]
}
```

#### Level 4: Advanced Content Extraction with Fallbacks

Handle dynamic content loading and provide multiple extraction strategies:

```json5
{
  "@url": "https://www.liberoquotidiano.it/",
  "@steps": [
    {
      "@xpath": "//a[contains(@href, '/news/') and contains(@href, 'gattuso')]",
      "@name": "giorgia_articles",
      "@fields": {
        "title": "./text()",
        "url": "./@href",
        "category": "substring-before(substring-after(./@href, '/news/'), '/')",
        "extraction_time": "current-dateTime()"
      },
      "@follow": {
        "@xpath": "./@href",
        "@steps": [
          {
            "@xpath": "//main | //article | //div[@id='main-content'] | //div[contains(@class, 'post-content')]",
            "@name": "article_details",
            "@fields": {
              "headline": ".//h1[1]/text() | .//header//h1/text() | .//title/text()",
              "subtitle": ".//h2[1]/text() | .//p[contains(@class, 'lead')]/text() | .//div[contains(@class, 'subtitle')]/text()",
              "full_content": "string-join(.//p[position() > 1 and not(contains(@class, 'share')) and not(contains(@class, 'related'))]//text(), ' ')",
              "paragraphs": ".//p[not(contains(@class, 'share')) and not(contains(@class, 'meta')) and normalize-space(text())]//text()",
              "author_name": ".//span[contains(@class, 'author')]/text() | .//div[contains(@class, 'byline')]//a/text() | .//meta[@name='author']/@content",
              "publish_datetime": ".//time[@datetime]/@datetime | .//meta[@property='article:published_time']/@content",
              "last_modified": ".//time[@class='updated']/@datetime | .//meta[@property='article:modified_time']/@content",
              "article_section": ".//nav//a[contains(@class, 'current')]/text() | .//meta[@property='article:section']/@content",
              "keywords": ".//meta[@name='keywords']/@content",
              "description": ".//meta[@name='description']/@content | .//meta[@property='og:description']/@content"
            }
          },
          {
            "@xpath": ".//img[not(contains(@class, 'ad')) and not(contains(@src, 'pixel'))]",
            "@name": "article_images",
            "@fields": {
              "src": "./@src | ./@data-src",
              "alt": "./@alt",
              "caption": "./following-sibling::figcaption/text() | ./parent::figure//figcaption/text()"
            }
          },
          {
            "@xpath": ".//div[contains(@class, 'comments')] | .//section[@id='comments']",
            "@name": "comments_section",
            "@fields": {
              "comments_count": "count(.//div[contains(@class, 'comment-content')] | .//article[contains(@class, 'comment')])",
              "comments_enabled": "boolean(.//form[contains(@class, 'comment-form')] | .//div[@id='respond'])"
            }
          }
        ]
      }
    }
  ]
}
```

## Anti-Scraping Challenges & Solutions

### Common Issues with Libero Quotidiano

1. **Dynamic Content Loading**
   - **Problem**: Content loaded via JavaScript after initial page load
   - **Solution**: Use `--xvfb` mode and add wait conditions

2. **Rate Limiting** 
   - **Problem**: IP blocking after too many requests
   - **Solution**: Add delays between requests, use respectful scraping practices

3. **Changing HTML Structure**
   - **Problem**: CSS classes and IDs change frequently
   - **Solution**: Use robust XPath expressions with multiple fallbacks

4. **JavaScript-Heavy Rendering**
   - **Problem**: Next.js dynamic content requires full browser execution  
   - **Solution**: Playwright handles this automatically, but may need longer wait times

### Running Anti-Scraping Examples

```bash
# Basic scraping with headless mode
dr-web-engine -q libero_basic.json5 -o results.json --xvfb -l info

# With extended logging for debugging
dr-web-engine -q libero_giorgia.json5 -o giorgia_articles.json --xvfb -l debug --log-file libero_scraping.log

# Respectful scraping with delays (add to automation scripts)
sleep 2 && dr-web-engine -q libero_content.json5 -o full_content.json --xvfb -l info
```

### Best Practices for Challenging Sites

#### 1. Robust XPath Strategies

```xpath
# Instead of specific classes that change:
//div[@class='article-123']

# Use content-based selection:
//div[contains(@class, 'article') or contains(@class, 'post')]

# Multiple fallback selectors:
//h1[@class='title'] | //h1[contains(@class, 'headline')] | //header//h1
```

#### 2. Content-Based Filtering

```xpath
# Case-insensitive text matching:
//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'giorgia')]

# Multiple keyword matching:
//a[contains(text(), 'Giorgia') or contains(text(), 'Meloni') or contains(text(), 'Premier')]

# Exclude unwanted content:
//p[not(contains(@class, 'advertisement')) and not(contains(@class, 'share'))]
```

#### 3. Respectful Scraping

```bash
# Add delays in automation scripts
for query in *.json5; do
    echo "Processing $query..."
    dr-web-engine -q "$query" -o "results_$(basename $query .json5).json" --xvfb
    echo "Waiting 5 seconds..."
    sleep 5
done
```

### Expected Results Structure

```json
{
  "giorgia_articles": [
    {
      "title": "Giorgia Meloni annuncia nuove misure economiche",
      "url": "/news/politica/44041234/giorgia-meloni-economia",
      "category": "politica",
      "article_details": {
        "headline": "Giorgia Meloni annuncia nuove misure economiche per il 2025",
        "full_content": "Il Presidente del Consiglio ha illustrato...",
        "author_name": "Redazione Libero",
        "publish_datetime": "2025-01-15T10:30:00+01:00",
        "article_section": "Politica"
      },
      "article_images": [
        {
          "src": "https://static.liberoquotidiano.it/...",
          "alt": "Giorgia Meloni durante la conferenza stampa"
        }
      ]
    }
  ]
}
```

### Troubleshooting Anti-Scraping Sites

1. **No Content Extracted**
   ```bash
   # Enable debug logging to see what's happening
   dr-web-engine -q query.json5 -o results.json --xvfb -l debug
   ```

2. **JavaScript Errors**
   ```bash
   # Check if Playwright can handle the site
   # Sometimes sites block headless browsers
   # Try without --xvfb for testing (opens visible browser)
   dr-web-engine -q query.json5 -o results.json -l debug
   ```

3. **Rate Limited/Blocked**
   ```bash
   # Add user agent and delays
   # This requires manual browser header inspection
   # Check network tab in browser dev tools for required headers
   ```

This example demonstrates real-world scraping challenges and provides multiple fallback strategies for robust data extraction from anti-scraping websites.

### 4. Fringe Domain: Lobste.rs

#### Level 1: Basic Story List with Dynamic Loading

```json5
{
  "@url": "https://lobste.rs",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".story",
      "@timeout": 10000
    },
    {
      "@type": "scroll",
      "@direction": "down",
      "@pixels": 500
    }
  ],
  "@steps": [
    {
      "@xpath": "//li[@class='story']",
      "@name": "stories",
      "@fields": {
        "title": ".//a[@class='u-url']/text()",
        "url": ".//a[@class='u-url']/@href",
        "domain": ".//span[@class='domain']/a/text()",
        "score": ".//div[@class='score']/text()",
        "tags": ".//a[@class='tag']/text()"
      }
    }
  ]
}
```

#### Level 2: Stories with Full Metadata

```json5
{
  "@url": "https://lobste.rs",
  "@steps": [
    {
      "@xpath": "//li[@class='story']",
      "@name": "stories",
      "@fields": {
        "title": ".//a[@class='u-url']/text()",
        "url": ".//a[@class='u-url']/@href",
        "external_url": ".//a[@class='u-url']/@href",
        "domain": ".//span[@class='domain']/a/text()",
        "score": ".//div[@class='score']/text()",
        "author": ".//a[@class='u-author']/text()",
        "time": ".//span[@class='timeago']/@title",
        "tags": ".//a[@class='tag']/text()",
        "comments_count": ".//a[@class='comments_label']/text()"
      }
    }
  ]
}
```

#### Level 3: Following to Comments

```json5
{
  "@url": "https://lobste.rs",
  "@steps": [
    {
      "@xpath": "//li[@class='story']",
      "@name": "stories", 
      "@fields": {
        "title": ".//a[@class='u-url']/text()",
        "story_url": ".//a[@class='comments_label']/@href"
      },
      "@follow": {
        "@xpath": ".//a[@class='comments_label']/@href",
        "@steps": [
          {
            "@xpath": "//div[@class='story_text']",
            "@name": "story_content",
            "@fields": {
              "description": ".//text()"
            }
          },
          {
            "@xpath": "//li[@class='comment']",
            "@name": "comments",
            "@fields": {
              "author": ".//a[@class='u-author']/text()",
              "time": ".//span[@class='timeago']/@title",
              "content": ".//div[@class='comment_text']//text()",
              "score": ".//div[@class='score']/text()",
              "depth": "./@style"
            }
          }
        ]
      }
    }
  ]
}
```

#### Level 4: Complex Nested Comments with Pagination

```json5
{
  "@url": "https://lobste.rs",
  "@steps": [
    {
      "@xpath": "//li[@class='story']",
      "@name": "stories",
      "@fields": {
        "title": ".//a[@class='u-url']/text()",
        "score": ".//div[@class='score']/text()",
        "tags": ".//a[@class='tag']/text()"
      },
      "@follow": {
        "@xpath": ".//a[@class='comments_label']/@href",
        "@steps": [
          {
            "@xpath": "//div[@class='story']",
            "@name": "story_details",
            "@fields": {
              "full_title": ".//h1/a/text()",
              "submitted_by": ".//span[@class='byline']/a[@class='u-author']/text()",
              "submitted_time": ".//span[@class='byline']//span[@class='timeago']/@title",
              "story_text": ".//div[@class='story_text']//text()"
            }
          },
          {
            "@xpath": "//li[contains(@class, 'comment')]",
            "@name": "all_comments",
            "@fields": {
              "id": "./@id",
              "author": ".//span[@class='byline']/a[@class='u-author']/text()",
              "time": ".//span[@class='byline']//span[@class='timeago']/@title",
              "content": ".//div[@class='comment_text']//text()",
              "score": ".//span[@class='score']/text()",
              "indent_level": "count(ancestor::li[contains(@class, 'comment')])",
              "parent_id": "./parent::li/@id",
              "upvotes": ".//a[@class='upvoter']/@title",
              "downvotes": ".//a[@class='downvoter']/@title"
            }
          }
        ]
      }
    }
  ],
  "@pagination": {
    "@xpath": "//a[@rel='next']/@href",
    "@limit": 5
  }
}
```

### 5. Form Interaction Examples

#### Search Form with Actions

Demonstrate form filling and submission:

```json5
{
  "@url": "https://quotes.toscrape.com/search.aspx",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@selector": "input[name='author']",
      "@timeout": 10000
    },
    {
      "@type": "fill",
      "@selector": "input[name='author']",
      "@value": "Einstein"
    },
    {
      "@type": "fill", 
      "@selector": "input[name='tag']",
      "@value": "inspirational"
    },
    {
      "@type": "click",
      "@selector": "input[type='submit']"
    },
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".quote",
      "@timeout": 10000
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='quote']",
      "@name": "search_results",
      "@fields": {
        "text": ".//span[@class='text']/text()",
        "author": ".//small[@class='author']/text()",
        "tags": ".//div[@class='tags']//a/text()"
      }
    }
  ]
}
```

#### Dropdown Interaction

Handle dropdown menus and hover effects:

```json5
{
  "@url": "https://example-with-dropdown.com",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".dropdown-trigger",
      "@timeout": 10000
    },
    {
      "@type": "hover",
      "@selector": ".dropdown-trigger"
    },
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".dropdown-menu",
      "@timeout": 5000
    },
    {
      "@type": "click",
      "@xpath": "//a[text()='Category 1']"
    },
    {
      "@type": "wait",
      "@until": "text",
      "@selector": "#selected-category",
      "@text": "Category 1",
      "@timeout": 5000
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='filtered-content']",
      "@name": "filtered_results",
      "@fields": {
        "title": ".//h3/text()",
        "content": ".//p/text()",
        "category": ".//span[@class='category']/text()"
      }
    }
  ]
}
```

#### Infinite Scroll with Load More Button

Combine scrolling and clicking for complete content loading:

```json5
{
  "@url": "https://infinite-scroll-with-button.com",
  "@actions": [
    {
      "@type": "wait",
      "@until": "element",
      "@selector": ".content-item",
      "@timeout": 10000
    },
    {
      "@type": "scroll",
      "@direction": "down",
      "@pixels": 800
    },
    {
      "@type": "wait",
      "@until": "element",
      "@selector": "#load-more-btn",
      "@timeout": 5000
    },
    {
      "@type": "click",
      "@selector": "#load-more-btn"
    },
    {
      "@type": "wait",
      "@until": "timeout",
      "@timeout": 3000
    },
    {
      "@type": "scroll",
      "@direction": "down",
      "@pixels": 800
    },
    {
      "@type": "click",
      "@selector": "#load-more-btn"
    },
    {
      "@type": "wait",
      "@until": "network-idle",
      "@timeout": 10000
    }
  ],
  "@steps": [
    {
      "@xpath": "//div[@class='content-item']",
      "@name": "all_content",
      "@fields": {
        "title": ".//h2/text()",
        "content": ".//p/text()",
        "timestamp": ".//time/@datetime",
        "author": ".//span[@class='author']/text()"
      }
    }
  ]
}
```

## Testing These Examples

### Running the Examples

Save any of these examples to a `.json5` file and run:

```bash
# Basic Hacker News scraping with actions
dr-web-engine -q hackernews_with_actions.json5 -o hn_results.json -l info --xvfb

# GitHub trending with dynamic loading
dr-web-engine -q github_trending_actions.json5 -o github_results.json -l debug --xvfb

# Complex Libero Quotidiano with anti-scraping handling
dr-web-engine -q libero_with_actions.json5 -o libero_results.json -l debug --log-file scraping.log --xvfb

# Form interaction example
dr-web-engine -q search_form_example.json5 -o search_results.json -l info --xvfb

# Infinite scroll with load more buttons
dr-web-engine -q infinite_scroll_actions.json5 -o infinite_results.json -l debug --xvfb
```

### Expected Challenges and Solutions

1. **Rate Limiting**: Add delays between requests in production
2. **Dynamic Content**: Use `@actions` with appropriate wait conditions
3. **Blocked Requests**: Some sites may block automated requests
4. **Structure Changes**: XPath selectors may need updates if sites change
5. **JavaScript Heavy Sites**: Always use `--xvfb` mode with action queries
6. **Timing Issues**: Adjust `@timeout` values based on site performance

### Action-Specific Tips

#### Wait Actions Best Practices
- Use `"@until": "element"` for waiting for content to load
- Use `"@until": "network-idle"` after form submissions
- Use `"@until": "text"` to wait for specific status messages
- Set appropriate timeouts (5-15 seconds for most cases)

#### Scroll Actions Best Practices  
- Scroll gradually (`500-800px` increments) for better stability
- Add wait delays between scrolls to allow content loading
- Use `"@selector"` to scroll to specific elements when possible

#### Click Actions Best Practices
- Prefer CSS selectors for modern sites, XPath for complex targeting
- Wait for elements to be present before clicking
- Add delays after clicks to allow page transitions

#### Fill Actions Best Practices
- Clear existing content by clicking first if needed
- Use specific selectors to target the exact input field
- Wait for form validation before proceeding to next steps

### Customization Tips

- **Adjust XPath selectors** based on current site structure
- **Add error handling** for missing elements
- **Implement respectful delays** for production use
- **Test selectors** in browser dev tools first

## JavaScript Execution (NEW in v0.9+)

Execute custom JavaScript code for complex scenarios that require dynamic logic, data manipulation, or advanced browser interactions beyond standard actions.

### JavaScript Actions
Execute JavaScript within the browser action pipeline for dynamic content manipulation:

```json5
{
  "@url": "https://dynamic-site.com",
  "@actions": [
    {
      "@type": "javascript",
      "@code": "window.loadMoreContent(); return document.querySelectorAll('.item').length;",
      "@wait-for": "document.querySelectorAll('.item').length > 5",
      "@timeout": 10000
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
  "@url": "https://spa-dashboard.com",
  "@steps": [
    {
      "@javascript": "return Array.from(document.querySelectorAll('.metric-card')).map(card => ({ name: card.querySelector('.metric-name').textContent.trim(), value: parseFloat(card.querySelector('.metric-value').textContent), trend: card.querySelector('.trend-indicator').className.includes('up') ? 'up' : 'down' }));",
      "@name": "metrics",
      "@return-json": true,
      "@timeout": 5000
    }
  ]
}
```

### Built-in JavaScript Utilities

DR Web Engine provides common utility functions in all JavaScript execution contexts:

```json5
{
  "@url": "https://e-commerce.com",
  "@steps": [
    {
      "@javascript": "return extractData('.product-card', { title: 'h3', price: '.price', rating: '.rating' });",
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

### Advanced Example: Infinite Scroll with Data Processing

```json5
{
  "@url": "https://social-feed.com",
  "@actions": [
    {
      "@type": "javascript",
      "@code": "let posts = []; let lastCount = 0; while (posts.length < 50) { await scrollAndWait(800, 2000); const currentPosts = document.querySelectorAll('.post'); if (currentPosts.length === lastCount) break; lastCount = currentPosts.length; } return lastCount;",
      "@timeout": 60000
    }
  ],
  "@steps": [
    {
      "@javascript": "return Array.from(document.querySelectorAll('.post')).map(post => { const timeEl = post.querySelector('.timestamp'); const timeAgo = timeEl ? timeEl.textContent : ''; const isRecent = timeAgo.includes('hour') || timeAgo.includes('minute'); return { author: post.querySelector('.author').textContent, content: post.querySelector('.content').textContent.substring(0, 200), timestamp: timeAgo, isRecent: isRecent, likes: parseInt(post.querySelector('.likes').textContent) || 0 }; });",
      "@name": "social_posts",
      "@return-json": true
    }
  ]
}
```

### JavaScript vs XPath: When to Use Each

**Use XPath when:**
- Simple text/attribute extraction
- Standard DOM traversal
- Performance is critical
- Query should be readable by non-developers

**Use JavaScript when:**
- Complex data processing or calculations
- Dynamic content manipulation
- Conditional logic based on element properties
- Integration with page JavaScript APIs
- Real-time data transformation

## JSON-LD Extraction (NEW in v1.0+)

Extract structured data directly from JSON-LD script tags embedded in web pages. This is often the cleanest way to get product information, article metadata, and business details.

### Basic JSON-LD Extraction

Many e-commerce sites include product information in structured format:

```json5
{
  "@url": "https://online-store.com/product/smartphone",
  "@steps": [
    {
      "@json-ld": {
        "@schema": "Product",
        "@fields": ["name", "description", "brand", "offers"]
      },
      "@name": "product_info"
    }
  ]
}
```

### Article Metadata Extraction

News sites and blogs often include rich article metadata:

```json5
{
  "@url": "https://tech-news.com/article/ai-breakthrough",
  "@steps": [
    {
      "@json-ld": {
        "@schema": "Article",
        "@fields": ["headline", "author", "datePublished", "articleBody"]
      },
      "@name": "article_data"
    }
  ]
}
```

### Business Information Extraction

Extract company details from business websites:

```json5
{
  "@url": "https://company.com/about",
  "@steps": [
    {
      "@json-ld": {
        "@schema": "Organization",
        "@fields": ["name", "address", "contactPoint", "url", "sameAs"]
      },
      "@name": "company_info"
    }
  ]
}
```

### Extract All Structured Data

Get all JSON-LD data regardless of schema type:

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

### JSON-LD Best Practices

**Check for JSON-LD availability:**
- View page source and search for `<script type="application/ld+json">`
- Use browser dev tools to inspect structured data
- Many sites use schema.org vocabulary

**Common Schema Types:**
- `Product` - E-commerce products
- `Article` - News articles, blog posts
- `Organization` - Companies, businesses
- `Person` - People, authors
- `Event` - Events, conferences
- `Recipe` - Cooking recipes
- `LocalBusiness` - Local businesses

**When to Use JSON-LD:**
- Site has structured data markup
- Need clean, semantically correct data
- Standard data types (products, articles, businesses)
- Want to avoid brittle XPath selectors

## API Extractor (NEW in v1.0+)

Capture data directly from AJAX/REST API calls that websites make to load dynamic content. This is powerful for extracting data that isn't visible in the initial HTML but is loaded asynchronously.

### Basic API Extraction

Many modern websites load product details via API calls:

```json5
{
  "@url": "https://shop.example.com/products/123",
  "@steps": [
    {
      "@api": {
        "@endpoint": "/api/products/\\d+",  // Regex to match product API
        "@method": "GET",
        "@response-type": "json",
        "@fields": ["id", "name", "price", "stock", "images"]
      },
      "@name": "product_data"
    }
  ]
}
```

### Search Results API

Extract search results that load dynamically:

```json5
{
  "@url": "https://search-site.com/search?q=smartphones",
  "@steps": [
    {
      "@api": {
        "@endpoint": "/api/search",
        "@response-type": "json",
        "@json-path": "$.data.results",  // Extract specific JSON path
        "@fields": ["title", "price", "rating", "availability"]
      },
      "@name": "search_results"
    }
  ]
}
```

### User Profile Data

Extract user information from social media or profile sites:

```json5
{
  "@url": "https://social-site.com/profile/username",
  "@steps": [
    {
      "@api": {
        "@endpoint": "/api/users/",
        "@response-type": "json",
        "@fields": ["username", "bio", "followers", "following", "posts"]
      },
      "@name": "profile_info"
    }
  ]
}
```

### Capture All API Calls

Monitor all API requests and responses:

```json5
{
  "@url": "https://dynamic-app.com",
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

### API Extractor Best Practices

**Identify API Endpoints:**
- Open browser developer tools (F12)
- Go to Network tab and filter by XHR/Fetch
- Reload the page and watch for API calls
- Note the URL patterns and response formats

**Common API Patterns:**
- `/api/products/123` - Product details
- `/api/search?q=query` - Search results
- `/api/users/profile` - User information
- `/api/reviews?product_id=123` - Reviews and ratings

**When to Use API Extractor:**
- Content loads dynamically via AJAX
- Data comes from REST/GraphQL APIs
- Site has infinite scroll or lazy loading
- XPath selectors miss dynamically loaded content
- Need live data updates

## Format Support

DR Web Engine supports both JSON5 and YAML formats:

- **JSON5**: More flexible JSON with comments and trailing commas
- **YAML**: Human-readable format with indentation-based structure

Choose the format that feels most comfortable for your use case.