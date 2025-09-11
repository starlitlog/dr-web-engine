# DR Web Engine Roadmap

This roadmap focuses on the core query engine capabilities needed for comprehensive deep web data extraction. The current version provides basic static extraction - this roadmap outlines the architectural enhancements to support dynamic, interactive web scraping.

## Current State (v0.9.0)

**What Works:**
- Static HTML extraction with XPath
- Basic pagination support
- **Enhanced multi-level navigation** with @follow (Kleene star patterns)
- JSON5/YAML query definitions
- **Browser Actions System** (click, scroll, wait, fill, hover, **javascript**)
- **Conditional Logic** (@if/@then/@else with multiple condition types)
- **🆕 JavaScript Execution** (actions and data extraction steps)
- **🆕 Modular Step Processor Architecture** (plugin-ready)
- **🆕 Plugin Registry System** with priority ordering
- Comprehensive test coverage (130+ tests)

**Completed Major Refactoring:**
- ✅ Modular step processor pipeline
- ✅ Plugin registry with lifecycle management
- ✅ Enhanced navigation with cycle detection
- ✅ JavaScript execution capabilities

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

## Phase 5: JavaScript Integration (v0.9.x) ✅ COMPLETE

**Priority: High** - Enable custom logic injection

**Status: ✅ COMPLETED in v0.9.0**

### 5.1 JavaScript Actions ✅ COMPLETE
Execute custom JS within browser actions:

```json5
{
  "@actions": [
    {
      "@type": "javascript",
      "@code": "window.loadMoreContent(); return document.querySelectorAll('.item').length;",
      "@wait-for": "document.querySelectorAll('.item').length > 10",
      "@timeout": 10000
    }
  ]
}
```

### 5.2 JavaScript Data Extraction ✅ COMPLETE
Execute JavaScript for data extraction steps:

```json5
{
  "@steps": [
    {
      "@javascript": "return Array.from(document.querySelectorAll('.item')).map(el => ({title: el.querySelector('h3').textContent, price: el.querySelector('.price').textContent}));",
      "@name": "products",
      "@return-json": true,
      "@timeout": 5000
    }
  ]
}
```

### 5.3 Built-in JavaScript Utilities ✅ COMPLETE
Common utility functions available:

```javascript
// Available in all JavaScript execution contexts
extractText(selector)              // Extract text from elements
extractAttribute(selector, attr)   // Extract attributes
extractData(selector, fields)      // Extract structured data  
waitForElements(selector, maxWait) // Wait for elements
scrollAndWait(pixels, waitTime)    // Scroll and wait
```

## Phase 4: Architecture Refactoring (v0.8.x) ✅ COMPLETE

**Priority: High** - Foundation for extensibility and multi-level navigation

**Status: ✅ COMPLETED in v0.8.0**

### 4.1 Step Processor Pipeline ✅ COMPLETE
Extracted step processing into modular, extensible system:

```python
class StepProcessor(ABC):
    @abstractmethod
    def can_handle(self, step) -> bool: ...
    
    @abstractmethod  
    def execute(self, context, page, step) -> List[Any]: ...

class ExtractStepProcessor(StepProcessor): ...
class ConditionalStepProcessor(StepProcessor): ...
class FollowStepProcessor(StepProcessor): ...
class JavaScriptStepProcessor(StepProcessor): ...
```

**Achieved Benefits:**
- ✅ Clean separation of concerns
- ✅ Foundation for plugins ready
- ✅ Easier testing and debugging
- ✅ Support for custom step types

### 4.2 Plugin Registry System ✅ COMPLETE
Implemented custom step processor system:

```python
class StepProcessorRegistry:
    def register(self, processor: StepProcessor): ...
    def find_processor(self, step): ...
    # Plus: priority ordering, lifecycle management, fast lookup
```

### 4.3 Enhanced Step Models ✅ COMPLETE
Implemented recursive navigation with full Kleene star support:

```python
class FollowStep(BaseModel):
    steps: List[Step]  # Union[ExtractStep, ConditionalStep, FollowStep, JavaScriptStep]  
    max_depth: Optional[int] = Field(default=3)
    detect_cycles: bool = Field(default=True)
    follow_external: bool = Field(default=False)
```

**Implementation Results:**
- ✅ **Incremental refactoring** - all tests passing throughout
- ✅ **Backward compatible** - no breaking API changes  
- ✅ **Safe rollback** - each increment was committable
- ✅ **Enhanced beyond original scope** - JavaScript execution added

---

## Implementation Priorities

### ✅ COMPLETED PHASES

**Phase 1 (Interaction & Dynamic Content)** ✅ v0.6.x
1. **Action System** ✅ - Browser interactions (click, scroll, wait, fill, hover)
2. **Wait Conditions** ✅ - Dynamic content handling
3. **Form Interactions** ✅ - Form filling and submission

**Phase 2 (Query Flow Control)** ✅ v0.7.x
1. **Conditional Logic** ✅ - Smart branching (@if/@then/@else)

**Phase 3 (Enhanced Navigation)** ✅ v0.8.x  
1. **Multi-Level Link Following** ✅ - Kleene star patterns
2. **Cycle Detection** ✅ - Prevent infinite loops
3. **Depth Control** ✅ - Limit crawling depth

**Phase 4 (Architecture Refactoring)** ✅ v0.8.x
1. **Step Processor Pipeline** ✅ - Modular, extensible system
2. **Plugin Registry System** ✅ - Priority ordering, lifecycle management
3. **Enhanced Step Models** ✅ - Recursive navigation support

**Phase 5 (JavaScript Integration)** ✅ v0.9.x
1. **JavaScript Actions** ✅ - Custom logic in browser interactions
2. **JavaScript Data Extraction** ✅ - JS-powered extraction steps
3. **Built-in Utilities** ✅ - Common helper functions

### 🚧 CURRENT PRIORITY

**Phase 6 (Plugin Ecosystem)** 🚧 v1.0.x - v1.2.x
1. **Plugin Foundation** 🎯 NEXT - Interface standards, CLI management
2. **Community Registry** - GitHub-based registry with voting
3. **Plugin Marketplace** - Commercial plugins, advanced ecosystem

## Phase 6: Plugin Ecosystem (v1.0.x) 🚧 NEXT PRIORITY

**Priority: High** - Enable community extensibility and specialized plugins

**Goal:** Create a thriving plugin ecosystem with community-driven development, voting system, and hybrid distribution strategy.

### 6.1 Plugin Foundation (v1.0.0)
Establish core plugin infrastructure and standards:

**Plugin Interface Standards**
```python
class StepProcessor(ABC):
    """Standard interface all step processors must implement"""
    @abstractmethod
    def can_handle(self, step) -> bool: ...
    
    @abstractmethod
    def execute(self, context, page, step) -> List[Any]: ...
    
    def get_supported_step_types(self) -> List[str]: ...
    def get_metadata(self) -> Dict[str, Any]: ...

class OutputProcessor(ABC):
    """New interface for output format plugins"""
    @abstractmethod
    def export(self, data: List[Dict], config: Dict) -> None: ...

class ActionHandler(ABC):
    """Extended interface for custom action handlers"""
    @abstractmethod
    def can_handle(self, action) -> bool: ...
    
    @abstractmethod
    def execute(self, page, action) -> Any: ...
```

**CLI Plugin Management**
```bash
# Discovery and installation
drweb plugin search "database"
drweb plugin install database-export
drweb plugin install github:user/custom-plugin

# Management
drweb plugin list --installed
drweb plugin update database-export
drweb plugin remove old-plugin
```

**Essential First Plugins (AI-Powered Extraction Workflow)**
- ✅ `smart-retry` - Intelligent retry logic with exponential backoff (v1.0.0)
- ✅ `proxy-rotation` - Enterprise proxy management with health monitoring (v1.0.0)
- ✅ `jsonld-extractor` - Extract structured data from JSON-LD scripts (v1.0.0)
- ✅ `api-extractor` - Integrate with REST APIs and AJAX endpoints (v1.0.0)
- ✅ `ai-selector` - AI-powered element detection and selection (v1.0.0)
- 🔄 `output-format-plugin` - JSONL/LLM-optimized structured outputs (v1.0.0)
- `intelligent-extraction` - LLM-powered page understanding and data extraction
- `pipeline-orchestration` - Enhanced data flow between extraction stages
- `auto-tagging` - AI-powered content classification and tagging
- `ai-validation` - LLM-based data quality and completeness validation
- `realtime-streaming` - Stream results between pipeline stages
- `drweb-ql-generator` - Natural language to DRWEB-QL conversion

### 6.2 Community Registry (v1.1.0)
GitHub-based plugin registry with community features:

**Registry Structure**
```
drweb-plugin-registry/
├── plugins.json              # Master plugin catalog
├── categories/
│   ├── extractors.json      # Data extraction plugins
│   ├── outputs.json         # Output format plugins
│   └── actions.json         # Browser action plugins
├── featured/
│   └── recommended.json     # Curated plugin recommendations
└── community/
    ├── requests.json        # Plugin requests with voting
    └── submissions.json     # Pending community submissions
```

**Community Voting System**
```bash
# Plugin requests and voting
drweb plugin request "Excel export with charts"
drweb plugin vote "database-export" 
drweb plugin submit ./my-plugin
```

**Plugin Metadata Format**
```json5
{
  "name": "database-export",
  "version": "1.0.0",
  "author": "DR Web Team",
  "description": "Export data to PostgreSQL, MySQL, MongoDB",
  "category": "output",
  "tags": ["database", "export", "sql"],
  "source": "pypi",  // or "github"
  "install": "pip install drweb-plugin-database-export",
  "repository": "https://github.com/drweb/plugin-database-export",
  "compatibility": ">=0.9.0",
  "votes": 42,
  "downloads": 1337
}
```

### 6.3 Plugin Marketplace (v1.2.0)
Advanced plugin ecosystem with commercial support:

**Hybrid Distribution Strategy**
- **Official Plugins:** PyPI with `drweb-plugin-` prefix
- **Community Plugins:** GitHub-based with registry metadata
- **Commercial Plugins:** Marketplace with licensing support

**Plugin Categories**

*Output Plugins:*
- `database-export` - Multi-database support (PostgreSQL, MySQL, MongoDB)
- `cloud-storage` - AWS S3, Google Cloud Storage, Azure Blob
- `excel-export` - Advanced Excel with charts, formatting, multiple sheets
- `api-webhook` - REST API integration with retry logic
- `csv-advanced` - Enhanced CSV with custom delimiters, encoding
- `json-transform` - Data transformation and schema mapping

*Extractor Plugins:*
- `table-extractor` - Smart table detection with header recognition
- `form-analyzer` - Complex form analysis and auto-filling
- `image-text-ocr` - OCR for text extraction from images
- `ai-selectors` - AI-powered element detection and classification
- `pdf-extractor` - Extract data from PDF documents
- `email-parser` - Parse structured data from emails

*Action Plugins:*
- `captcha-solver` - Integration with 2captcha, Anti-Captcha services
- `auth-manager` - OAuth, SAML, multi-factor authentication flows
- `visual-actions` - Image-based clicking and visual recognition
- `screenshot-tools` - Advanced screenshot capture and comparison
- `performance-monitor` - Page performance metrics and monitoring

*Advanced Features:*
- Plugin dependency management
- Plugin version compatibility checking
- Plugin metrics and analytics
- Commercial plugin marketplace
- Plugin development toolkit

**Success Metrics**
- 20+ community-contributed plugins by v1.2.0
- Active plugin request/voting system
- Plugin development documentation and examples
- Commercial plugin partner ecosystem

---

## Implementation Timeline

### Current Status (v0.9.0) ✅ COMPLETE
- **Foundation Architecture:** Modular step processors, plugin registry
- **Core Features:** JavaScript execution, Kleene star navigation, conditional logic
- **Extensibility:** Plugin-ready architecture with priority system

### Next Major Milestones

**v1.0.0 - Plugin Foundation** 🚧 IN PROGRESS  
- ✅ Plugin interface standards (StepProcessor, OutputProcessor, ActionHandler)
- ✅ JSON-LD Extractor plugin (structured data extraction)
- ✅ API Extractor plugin (AJAX/REST integration)  
- ✅ AI-Selector plugin (intelligent element detection)
- ✅ Smart Retry plugin (intelligent retry with backoff)
- ✅ Proxy Rotation plugin (enterprise proxy management)
- 🔄 Output Format plugin (JSONL/LLM-optimized outputs) - **CURRENT PRIORITY**
- CLI plugin management
- Plugin development documentation

**AI-Powered Extraction Workflow Journey:**
```
Natural Language → DRWEB-QL Generator → Intelligent Extraction → 
JSONL Output → Pipeline Orchestration → AI Validation → Auto-Tagging → 
Real-time Streaming
```

**v1.1.0 - Community Registry** (Q3 2025)  
- GitHub-based plugin registry
- Community voting system
- Plugin submission process
- 10+ community plugins

**v1.2.0 - Plugin Marketplace** (Q4 2025)
- Advanced plugin ecosystem
- Commercial plugin support
- Plugin metrics and analytics
- 20+ available plugins

### Long-term Vision (v2.0+)
- AI-powered plugin recommendations
- Visual plugin development tools
- Enterprise plugin management
- Global plugin marketplace

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