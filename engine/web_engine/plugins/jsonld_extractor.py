"""
JSON+LD Extractor Plugin for DR Web Engine.
Extracts structured data from JSON-LD script tags on web pages.
"""

import json
import logging
from typing import Any, List, Dict, Optional

from ..processors import StepProcessor
from ..models import JsonLdStep

logger = logging.getLogger(__name__)




class JsonLdExtractorProcessor(StepProcessor):
    """Processes JSON-LD extraction steps."""
    
    def __init__(self):
        super().__init__()
        self.priority = 25  # Higher precedence than most processors
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is a JSON-LD step."""
        return isinstance(step, JsonLdStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return ["JsonLdStep"]
    
    def execute(self, context: Any, page: Any, step: JsonLdStep) -> List[Any]:
        """Extract JSON-LD structured data from the page."""
        try:
            self.logger.info("Extracting JSON-LD structured data")
            
            # Find all JSON-LD script tags
            script_elements = page.query_selector_all('script[type="application/ld+json"]')
            
            if not script_elements:
                self.logger.warning("No JSON-LD script tags found on page")
                return []
            
            all_structured_data = []
            
            for script in script_elements:
                try:
                    # Get the script content
                    script_content = script.text_content()
                    if not script_content.strip():
                        continue
                    
                    # Parse JSON-LD
                    structured_data = json.loads(script_content)
                    
                    # Handle arrays of structured data
                    if isinstance(structured_data, list):
                        all_structured_data.extend(structured_data)
                    else:
                        all_structured_data.append(structured_data)
                        
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse JSON-LD script: {e}")
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing JSON-LD script: {e}")
                    continue
            
            if not all_structured_data:
                self.logger.warning("No valid JSON-LD data found")
                return []
            
            # Filter and process the structured data
            results = self._process_structured_data(all_structured_data, step)
            
            self.logger.info(f"Extracted {len(results)} JSON-LD items")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to extract JSON-LD data: {e}")
            return []
    
    def _process_structured_data(self, data: List[Dict], step: JsonLdStep) -> List[Dict]:
        """Process and filter structured data based on step configuration."""
        results = []
        
        for item in data:
            # Handle @graph structures (common in JSON-LD)
            if isinstance(item, dict) and '@graph' in item:
                # Process each item in the graph
                for graph_item in item['@graph']:
                    processed = self._process_single_item(graph_item, step)
                    if processed:
                        results.append(processed)
            else:
                processed = self._process_single_item(item, step)
                if processed:
                    results.append(processed)
        
        return results
    
    def _process_single_item(self, item: Dict, step: JsonLdStep) -> Optional[Dict]:
        """Process a single structured data item."""
        if not isinstance(item, dict):
            return None
        
        # Filter by schema type if specified
        if step.schema_type:
            item_type = item.get('@type', '')
            # Handle both simple types and URLs
            if isinstance(item_type, str):
                if not (step.schema_type in item_type or item_type.endswith('/' + step.schema_type)):
                    return None
            elif isinstance(item_type, list):
                # Check if any type matches
                if not any(step.schema_type in t or t.endswith('/' + step.schema_type) for t in item_type):
                    return None
        
        # Extract specific fields if specified
        if step.fields:
            result = {}
            for field in step.fields:
                if field in item:
                    result[field] = self._clean_value(item[field])
            return result if result else None
        else:
            # Return all data, cleaned
            return self._clean_item(item)
    
    def _clean_item(self, item: Dict) -> Dict:
        """Clean a structured data item for output."""
        cleaned = {}
        
        for key, value in item.items():
            # Skip JSON-LD specific keys unless they're useful
            if key.startswith('@') and key not in ['@type', '@id']:
                continue
            
            cleaned[key] = self._clean_value(value)
        
        return cleaned
    
    def _clean_value(self, value: Any) -> Any:
        """Clean a value for output."""
        if isinstance(value, dict):
            # Handle nested objects (like addresses, offers, etc.)
            if '@type' in value:
                # It's a structured object, clean it
                return self._clean_item(value)
            else:
                # Regular dict, clean recursively
                return {k: self._clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Clean list items
            return [self._clean_value(item) for item in value]
        else:
            # Primitive value, return as-is
            return value


# Example usage queries:

JSONLD_EXAMPLES = {
    "product_data": {
        "@url": "https://example-store.com/product/123",
        "@steps": [
            {
                "@json-ld": {
                    "@schema": "Product",
                    "@fields": ["name", "price", "availability", "brand", "description"]
                },
                "@name": "product_info"
            }
        ]
    },
    
    "article_data": {
        "@url": "https://news-site.com/article/456", 
        "@steps": [
            {
                "@json-ld": {
                    "@schema": "Article",
                    "@fields": ["headline", "author", "datePublished", "articleBody"]
                },
                "@name": "article_metadata"
            }
        ]
    },
    
    "organization_data": {
        "@url": "https://company.com/about",
        "@steps": [
            {
                "@json-ld": {
                    "@schema": "Organization",
                    "@fields": ["name", "address", "contactPoint", "sameAs"]
                },
                "@name": "company_info"
            }
        ]
    },
    
    "all_structured_data": {
        "@url": "https://example.com",
        "@steps": [
            {
                "@json-ld": {
                    "@all-schemas": True
                },
                "@name": "all_structured_data"
            }
        ]
    }
}