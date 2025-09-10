# Plugin Examples

Examples demonstrating DR Web Engine's plugin system for advanced data extraction.

## Examples

### `jsonld_extraction.json5`
**Purpose**: Extract structured data from JSON-LD script tags  
**Demonstrates**: 
- Product schema extraction
- Organization data extraction  
- All schema types extraction
**Best for**: E-commerce sites, business directories, news sites with structured markup

### `api_extraction.json5`
**Purpose**: Intercept and extract data from AJAX/REST API calls  
**Demonstrates**:
- Product API endpoint monitoring
- Search results API capture
- User profile API extraction
- General API call interception
**Best for**: SPAs, dynamic content, real-time data

## Plugin Features

### JSON-LD Extractor
- **Schema filtering**: Extract specific schema.org types
- **Field selection**: Get only the fields you need
- **All schemas**: Capture all structured data
- **Clean output**: Automatically removes JSON-LD metadata

### API Extractor  
- **Endpoint patterns**: Use regex to match specific APIs
- **Response filtering**: Extract specific fields from API responses
- **JSONPath support**: Navigate complex JSON structures
- **Multiple formats**: Handle JSON, XML, and text responses

## Usage Tips

**JSON-LD**:
- Check page source for `<script type="application/ld+json">` tags
- Use browser dev tools to inspect structured data
- Common schemas: Product, Article, Organization, Person

**API Extractor**:
- Open browser Network tab to identify API endpoints
- Filter by XHR/Fetch to see AJAX calls
- Note URL patterns and response structures
- Test with general capture first, then add specific filters