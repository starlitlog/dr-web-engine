# DR Web Engine Roadmap

This roadmap focuses on the core query engine capabilities needed for comprehensive deep web data extraction. The current version provides basic static extraction - this roadmap outlines the architectural enhancements to support dynamic, interactive web scraping.

## Current State (v0.7.0)

**What Works:**
- Static HTML extraction with XPath
- Basic pagination support
- Single-level link following (@follow)
- JSON5/YAML query definitions
- **NEW**: Browser Actions System (click, scroll, wait, fill, hover)
- **NEW**: Conditional Logic (@if/@then/@else with multiple condition types)
- Comprehensive test coverage (95+ tests)

**Core Limitations:**
- Single-threaded, monolithic architecture
- Limited extensibility for new step types
- No loop constructs yet
- No variable system
- No parallel execution

---

## Phase 1: Interaction & Dynamic Content (v0.6.x) ✅ COMPLETE

**Priority: Critical** - Modern web apps require interaction flows

**Status: ✅ COMPLETED in v0.6.1**

### 1.1 Action System
Add support for browser interactions within queries:

```json5
{
  "@url": "https://example.com",
  "@actions": [
    {"@type": "click", "@selector": "#load-more-btn"},
    {"@type": "scroll", "@direction": "down", "@pixels": 500},
    {"@type": "wait", "@until": "element", "@selector": ".content-loaded"}
  ],
  "@steps": [...]
}
```

**New Keywords:**
- `@actions` - Pre-extraction actions
- `@type` - Action type (click, scroll, hover, fill)
- `@wait` - Wait conditions (element, timeout, custom)
- `@until` - Wait criteria

**Implementation:**
- Create `ActionProcessor` class
- Add action models to `models.py`
- Extend engine to support pre-step actions

### 1.2 Wait Conditions
Advanced waiting for dynamic content:

```json5
{
  "@wait": {
    "@type": "element",
    "@selector": ".dynamic-content",
    "@timeout": 10000
  }
}
```

**Wait Types:**
- `element` - Wait for element to appear/disappear
- `text` - Wait for specific text content
- `attribute` - Wait for attribute changes
- `count` - Wait for element count threshold
- `custom` - JavaScript-based conditions

### 1.3 Form Interactions
Support for form filling and submission:

```json5
{
  "@form": {
    "@selector": "#search-form",
    "@fields": {
      "query": "search term",
      "category": "option:electronics"
    },
    "@submit": true
  }
}
```

---

## Phase 2: Query Flow Control (v0.7.x)

**Priority: High** - Enable complex extraction workflows

**Status: Phase 2.1 ✅ COMPLETED in v0.7.0**

### 2.1 Conditional Logic ✅ COMPLETE
Branching execution based on page content:

```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@if": {"@exists": "#premium-content"},
      "@then": [
        {"@xpath": "//div[@class='premium']", "@fields": {...}}
      ],
      "@else": [
        {"@xpath": "//div[@class='free']", "@fields": {...}}
      ]
    }
  ]
}
```

**Implemented Keywords:**
- `@if/@then/@else` - Conditional execution steps
- `@exists/@not-exists` - Element existence checks
- `@contains` - Text content checks
- `@count/@min-count/@max-count` - Element count conditions

**Phase 2 Status: ✅ COMPLETE**

Phase 2.2 (Loop Constructs) and 2.3 (Variable System) have been **removed from roadmap** as they are redundant:
- **Loops**: XPath naturally processes arrays; actions + pagination handle dynamic loading
- **Variables**: Over-engineering for current use cases; can be added later if needed

---

## Phase 3: Multi-Level Navigation (v0.8.x) 

**Priority: Medium** - Enhanced link following (Kleene star)

**Note: Redesigned after Phase 4 architecture improvements**

### 3.1 Multi-Level Navigation
Beyond single @follow:

```json5
{
  "@navigation": {
    "@strategy": "breadth-first",
    "@max-depth": 3,
    "@flow": [
      {
        "@from": "category-pages",
        "@follow": ".//a[@class='product-link']",
        "@to": "product-pages"
      },
      {
        "@from": "product-pages", 
        "@follow": ".//a[@class='review-link']",
        "@to": "review-pages"
      }
    ]
  }
}
```

**Navigation Strategies:**
- `breadth-first` - Crawl all at depth N before N+1
- `depth-first` - Follow links as deep as possible
- `priority` - Order by custom scoring

### 3.2 State Management
Preserve context across navigation:

```json5
{
  "@context": {
    "@preserve": ["session", "cookies", "local-storage"],
    "@share-across": "all-pages"
  }
}
```

### 3.3 Smart Link Discovery
Automatic link detection and classification:

```json5
{
  "@discover": {
    "@patterns": ["pagination", "detail-pages", "categories"],
    "@auto-follow": true,
    "@rules": [
      {"@pattern": "product-\\d+", "@type": "product-page"},
      {"@pattern": "category/.*", "@type": "category-page"}
    ]
  }
}
```

---

## Phase 4: Architecture Refactoring (v0.9.x)

**Priority: High** - Enable extensibility and plugins

### 4.1 Step Processor Pipeline
Replace monolithic engine with pluggable processors:

```python
# Current: Hard-coded in engine.py
def execute_step(context, page, step):
    # All logic baked in

# New: Pluggable processors
class StepProcessorRegistry:
    processors = {
        'xpath': XPathStepProcessor,
        'action': ActionStepProcessor,
        'condition': ConditionalStepProcessor,
        'loop': LoopStepProcessor
    }
```

### 4.2 Extension Points
Well-defined plugin interfaces:

```python
class StepProcessor(ABC):
    @abstractmethod
    def can_handle(self, step: Dict) -> bool:
        pass
    
    @abstractmethod
    def process(self, context: ExecutionContext, step: Dict) -> Any:
        pass

class ActionHandler(ABC):
    @abstractmethod
    def execute_action(self, page: Page, action: Dict) -> None:
        pass
```

### 4.3 Dynamic Schema System
Extensible query models:

```python
# Current: Fixed Pydantic models
class ExtractStep(BaseModel):
    xpath: str = Field(alias="@xpath")
    # Fixed fields

# New: Dynamic field registration
class ExtensibleStep(BaseModel):
    step_type: str
    config: Dict[str, Any]  # Dynamic based on step_type
```

### 4.4 Plugin Architecture
```python
class DrWebEnginePlugin(ABC):
    @abstractmethod
    def register_step_processors(self, registry: StepProcessorRegistry):
        pass
    
    @abstractmethod
    def register_action_handlers(self, registry: ActionHandlerRegistry):
        pass
```

---

## Phase 5: Advanced Features (v1.0.x)

**Priority: Medium** - Power-user capabilities

### 5.1 JavaScript Execution
Execute custom JS for complex scenarios:

```json5
{
  "@javascript": {
    "@code": "window.loadMoreContent(); return document.querySelectorAll('.item').length;",
    "@wait-for": "return-value > 10"
  }
}
```

### 5.2 Multi-Tab/Window Support
Coordinate across browser contexts:

```json5
{
  "@tabs": {
    "main": {"@url": "https://example.com"},
    "reference": {"@url": "https://reference.com"}
  },
  "@cross-reference": {
    "@from": "main",
    "@to": "reference",
    "@lookup": "product-id"
  }
}
```

### 5.3 Advanced Selectors
Beyond XPath:

```json5
{
  "@selectors": [
    {"@type": "xpath", "@expression": "//div[@class='item']"},
    {"@type": "css", "@expression": "div.item"},
    {"@type": "text", "@contains": "Product Name"},
    {"@type": "visual", "@image": "button-template.png"}
  ]
}
```

## Phase 4: Architecture Refactoring (v0.8.x) 🚧 CURRENT

**Priority: High** - Foundation for extensibility and multi-level navigation

**Status: Ready to start after v0.7.0**

### 4.1 Step Processor Pipeline ⭐ NEXT
Extract step processing into modular, extensible system:

```python
class StepProcessor(ABC):
    @abstractmethod
    def can_handle(self, step) -> bool: ...
    
    @abstractmethod  
    def execute(self, context, page, step) -> List[Any]: ...

class ExtractStepProcessor(StepProcessor): ...
class ConditionalStepProcessor(StepProcessor): ...
```

**Benefits:**
- Clean separation of concerns
- Foundation for plugins  
- Easier testing and debugging
- Support for custom step types

### 4.2 Plugin Registry System
Enable custom step processors:

```python
class StepProcessorRegistry:
    def register(self, processor: StepProcessor): ...
    def find_processor(self, step): ...
```

### 4.3 Enhanced Step Models
Support recursive navigation:

```python
class FollowStep(BaseModel):
    steps: List[Step]  # Union[ExtractStep, ConditionalStep, FollowStep]  
    max_depth: Optional[int] = Field(default=3)
    detect_cycles: bool = Field(default=True)
```

**Implementation Approach:**
- ✅ **Incremental refactoring** - each phase maintains all tests passing
- ✅ **Backward compatible** - no API changes  
- ✅ **Safe rollback** - each increment is committable

---

## Implementation Priorities

### Phase 1 (Next Release - Critical)
1. **Action System** - Essential for modern web apps
2. **Wait Conditions** - Required for dynamic content
3. **Form Interactions** - Common use case

### Phase 2 (High Impact) ✅ COMPLETE
1. **Conditional Logic** ✅ - Enables complex scenarios (v0.7.0)

### Phase 4 (Foundation) 🚧 NEXT PRIORITY
1. **Step Processor Pipeline** - Enables all other features
2. **Plugin System** - Critical for long-term extensibility
3. **Enhanced Step Models** - Support for recursive navigation

### Phase 3 (Enhanced Navigation)
1. **Multi-Level Link Following** - Kleene star patterns
2. **Cycle Detection** - Prevent infinite loops  
3. **Depth Control** - Limit crawling depth

### Phases 5+ (Future)
- Advanced navigation strategies
- Performance optimizations
- Community plugin ecosystem
- JavaScript execution
- Multi-tab coordination
- Visual selectors

---

## Technical Considerations

### Backward Compatibility
- All existing v0.5.6b queries must continue working
- New features are additive (optional keywords)
- Deprecation warnings for any breaking changes

### Performance
- Maintain single-threaded execution model initially
- Optimize for memory usage during deep navigation
- Add performance monitoring hooks

### Testing Strategy
- Comprehensive test suite for each new feature
- Integration tests with real websites
- Regression testing for existing functionality

### Documentation
- Update query syntax documentation
- Add migration guides for new features
- Provide comprehensive examples

---

## Success Metrics

**Phase 1 Success:**
- Can handle 90% of modern dynamic web applications
- Support for major SPA frameworks (React, Vue, Angular)
- Form-based authentication flows

**Phase 2 Success:**
- Complex multi-step extraction workflows
- Conditional data extraction based on page content
- Variable-driven dynamic queries

**Overall Success (v1.0):**
- Extensible plugin ecosystem
- Community-contributed step processors
- Enterprise-grade deep web extraction capabilities

This roadmap transforms DR Web Engine from a static HTML extractor into a comprehensive deep web data extraction platform while maintaining its core philosophy of raw extraction with post-processing flexibility.