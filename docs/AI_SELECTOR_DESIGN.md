# AI-Selector Plugin Design Document

## Overview
The AI-Selector plugin enables intelligent element detection using natural language descriptions and AI-powered understanding of web page structure and semantics.

## Core Architecture

### 1. Natural Language Element Selection

Users describe elements in plain English instead of technical selectors:

```json5
{
  "@ai-select": {
    "@find": "the main product title",
    "@context": "product details section", 
    "@type": "text"
  }
}
```

### 2. Multi-Modal Understanding

The plugin would use multiple approaches:

#### A. DOM Analysis
- Convert DOM to structured representation
- Extract semantic HTML5 tags (article, nav, main, etc.)
- Analyze class/id naming patterns
- Identify common patterns (BEM, semantic naming)

#### B. Visual Analysis  
- Take page screenshots
- Use vision models to identify regions
- Understand visual hierarchy
- Detect UI patterns (cards, lists, forms)

#### C. Content Analysis
- Analyze text content and context
- Identify data types (prices, dates, emails)
- Understand content relationships
- Detect patterns across similar elements

## Implementation Approaches

### Approach 1: LLM-Based Selection (Recommended)

```python
class AISelectProcessor(StepProcessor):
    def __init__(self, model_provider="openai"):
        self.llm = self._initialize_llm(model_provider)
        
    def execute(self, context, page, step: AiSelectStep):
        # 1. Extract page context
        dom_context = self._extract_dom_context(page)
        visual_context = self._capture_visual_context(page)
        
        # 2. Build prompt
        prompt = self._build_selection_prompt(
            find=step.find,
            context=step.context_hint,
            dom=dom_context,
            visual=visual_context
        )
        
        # 3. Get AI selection
        selection = self.llm.select_elements(prompt)
        
        # 4. Convert to XPath/CSS
        selectors = self._convert_to_selectors(selection)
        
        # 5. Extract with confidence scoring
        return self._extract_with_confidence(page, selectors)
```

### Approach 2: Embedding-Based Similarity

```python
class SemanticMatcher:
    def find_similar_elements(self, description, page_elements):
        # 1. Embed the description
        target_embedding = self.embed(description)
        
        # 2. Embed all page elements
        element_embeddings = [
            self.embed(self._element_to_text(el)) 
            for el in page_elements
        ]
        
        # 3. Find most similar
        similarities = cosine_similarity(target_embedding, element_embeddings)
        
        # 4. Return top matches above threshold
        return self._get_top_matches(similarities, threshold=0.7)
```

### Approach 3: Hybrid Rule + AI

Combine deterministic rules with AI for reliability:

```python
class HybridSelector:
    def select(self, description, page):
        # 1. Try rule-based patterns first
        if result := self._try_common_patterns(description, page):
            return result
            
        # 2. Fall back to AI
        return self._ai_select(description, page)
    
    def _try_common_patterns(self, description, page):
        patterns = {
            "price": ["//span[contains(@class, 'price')]", "//div[@itemprop='price']"],
            "title": ["//h1", "//h2[@class='title']", "//div[@itemprop='name']"],
            "image": ["//img[@class='product-image']", "//div[@class='gallery']//img"],
        }
        # Check if description matches known patterns
```

## Query Syntax Design

### Basic Natural Language
```json5
{
  "@ai-select": "product prices"  // Simple string
}
```

### Structured Queries
```json5
{
  "@ai-select": {
    "@find": "product prices including discounts",
    "@context": "main content area, not sidebar",
    "@type": "currency",
    "@count": "all",  // all, first, last, exactly(n)
    "@confidence": 0.8
  }
}
```

### Learning from Examples
```json5
{
  "@ai-select": {
    "@find": "product reviews",
    "@examples": [
      "Great product, highly recommend!",
      "★★★★★ Amazing quality"
    ],
    "@exclude": ["advertisement", "sponsored"]
  }
}
```

### Visual Descriptions
```json5
{
  "@ai-select": {
    "@find": "the red 'Add to Cart' button",
    "@visual": {
      "@position": "below product image",
      "@color": "red", 
      "@type": "button"
    }
  }
}
```

## Use Cases

### 1. Cross-Site Data Extraction
Single query works across different e-commerce sites:
```json5
{
  "@ai-select": {
    "@find": "product name, price, and availability",
    "@adapt": true  // Adapts to different site structures
  }
}
```

### 2. Dynamic Structure Handling
Handles sites that change their HTML structure:
```json5
{
  "@ai-select": {
    "@find": "news article headlines",
    "@fallback": "any h2 or h3 in main content"
  }
}
```

### 3. Complex Relationships
Understanding element relationships:
```json5
{
  "@ai-select": {
    "@find": "prices next to product names",
    "@relationship": "sibling",
    "@within": "product cards"
  }
}
```

### 4. Content-Based Selection
Select based on content meaning:
```json5
{
  "@ai-select": {
    "@find": "negative reviews",
    "@sentiment": "negative",
    "@min_length": 50
  }
}
```

## Technical Implementation

### Required Components

1. **Model Integration**
   - OpenAI GPT-4V for vision + text
   - Claude for complex reasoning
   - Local models (LLaMA, BERT) for privacy
   - Embeddings (text-embedding-ada-002)

2. **Context Extraction**
   ```python
   def extract_context(page):
       return {
           "dom": page.content(),
           "screenshot": page.screenshot(),
           "metadata": extract_metadata(page),
           "structure": analyze_structure(page)
       }
   ```

3. **Caching Layer**
   - Cache AI selections for similar pages
   - Store embedding vectors
   - Learn from user corrections

4. **Confidence Scoring**
   ```python
   def score_selection(element, description):
       scores = {
           "semantic": semantic_similarity(element, description),
           "visual": visual_match_score(element, description),
           "structural": structural_score(element),
           "type": type_match_score(element, expected_type)
       }
       return weighted_average(scores)
   ```

## API Examples

### Simple Price Extraction
```json5
{
  "@url": "https://any-store.com/product/123",
  "@steps": [
    {
      "@ai-select": "the main product price, including any sale price",
      "@name": "price"
    }
  ]
}
```

### Review Extraction with Sentiment
```json5
{
  "@url": "https://reviews-site.com/product",
  "@steps": [
    {
      "@ai-select": {
        "@find": "customer reviews",
        "@extract": {
          "text": "review content",
          "rating": "star rating or score",
          "author": "reviewer name",
          "sentiment": "@analyze"  // AI analyzes sentiment
        }
      },
      "@name": "reviews"
    }
  ]
}
```

### Adaptive Multi-Site Extraction
```json5
{
  "@url": "https://unknown-ecommerce.com",
  "@steps": [
    {
      "@ai-select": {
        "@template": "ecommerce_product",  // Pre-trained template
        "@extract": ["name", "price", "description", "images", "availability"],
        "@confidence": 0.7,
        "@max_attempts": 3
      },
      "@name": "product_data"
    }
  ]
}
```

## Challenges & Solutions

### Challenge 1: Accuracy
**Solution**: Multi-modal verification
- Cross-check visual and DOM selection
- Use confidence thresholds
- Provide fallback selectors

### Challenge 2: Performance  
**Solution**: Intelligent caching
- Cache selections for similar pages
- Pre-compute embeddings
- Use lightweight models for simple selections

### Challenge 3: Cost
**Solution**: Tiered approach
- Try rule-based first
- Use small models for simple tasks
- Reserve large models for complex cases

### Challenge 4: Privacy
**Solution**: Local model option
- Support local LLMs
- On-device processing option
- No data sent to external APIs

## Integration with DR Web Engine

### Model Configuration
```python
# In engine configuration
AI_SELECTOR_CONFIG = {
    "provider": "openai",  # openai, anthropic, local
    "model": "gpt-4-vision-preview",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "cache_enabled": True,
    "confidence_threshold": 0.7,
    "fallback_to_xpath": True
}
```

### Usage in Pipeline
```python
class WebEngine:
    def __init__(self):
        self.processors = [
            XPathProcessor(),
            AISelectProcessor(),  # New AI processor
            ConditionalProcessor(),
            # ...
        ]
```

## Performance Considerations

### Optimization Strategies

1. **Batch Processing**
   - Group similar selections
   - Single API call for multiple elements

2. **Progressive Enhancement**
   - Start with fast, simple matching
   - Upgrade to AI if needed

3. **Result Caching**
   ```python
   @lru_cache(maxsize=1000)
   def ai_select_cached(description, page_hash):
       return ai_select(description, page_hash)
   ```

4. **Parallel Processing**
   - Process multiple elements concurrently
   - Stream results as available

## Future Enhancements

### Phase 1: Basic Implementation
- Natural language element selection
- OpenAI GPT-4V integration
- Confidence scoring

### Phase 2: Advanced Features  
- Multi-model support
- Learning from corrections
- Template library

### Phase 3: Intelligence Layer
- Cross-site adaptation
- Automatic schema detection
- Self-improving selections

### Phase 4: Enterprise Features
- Custom model training
- Private deployment
- Audit trails

## Example Implementation Timeline

**Week 1-2**: Core Architecture
- Design model abstraction layer
- Implement basic prompt engineering
- Create AiSelectStep model

**Week 3-4**: Model Integration
- Integrate OpenAI API
- Add vision capabilities
- Implement confidence scoring

**Week 5-6**: Testing & Optimization
- Build test suite
- Optimize performance
- Add caching layer

**Week 7-8**: Documentation & Release
- Write user documentation
- Create example library
- Package for release

## Conclusion

The AI-Selector plugin would revolutionize web scraping by:
1. Making it accessible to non-technical users
2. Handling dynamic and changing websites
3. Enabling true cross-site extraction
4. Reducing maintenance burden
5. Providing intelligent data understanding

This would position DR Web Engine as the most advanced and user-friendly web scraping tool available.