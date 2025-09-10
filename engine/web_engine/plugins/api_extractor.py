"""
API Extractor Plugin for DR Web Engine.
Intercepts and extracts data from API calls made by web pages.
"""

import json
import logging
import re
import asyncio
from typing import Any, List, Dict, Optional
from urllib.parse import urljoin, urlparse

from ..processors import StepProcessor
from ..models import ApiStep

logger = logging.getLogger(__name__)


class ApiExtractorProcessor(StepProcessor):
    """Processes API extraction steps by monitoring network requests."""
    
    def __init__(self):
        super().__init__()
        self.priority = 30  # Higher priority than most processors
        self.intercepted_requests = []
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is an API step."""
        return isinstance(step, ApiStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return ["ApiStep"]
    
    def execute(self, context: Any, page: Any, step: ApiStep) -> List[Any]:
        """Monitor network requests and extract API data."""
        try:
            self.logger.info("Starting API extraction")
            
            # Set up network monitoring
            self._setup_network_monitoring(page, step)
            
            # Wait for API calls to be made (trigger page interactions if needed)
            self._wait_for_api_calls(page, step)
            
            # Process intercepted requests
            results = self._process_intercepted_requests(step)
            
            self.logger.info(f"Extracted data from {len(results)} API calls")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to extract API data: {e}")
            return []
    
    def _setup_network_monitoring(self, page: Any, step: ApiStep) -> None:
        """Set up network request/response monitoring."""
        self.intercepted_requests = []
        
        def handle_response(response):
            """Handle network responses."""
            try:
                url = response.url
                method = response.request.method
                status = response.status
                
                # Check if this matches our endpoint pattern
                if self._matches_endpoint_pattern(url, step.endpoint_pattern):
                    # Only process successful responses
                    if 200 <= status < 300:
                        # Get response body asynchronously
                        asyncio.create_task(
                            self._process_response(response, step)
                        )
                        
            except Exception as e:
                self.logger.warning(f"Error processing response: {e}")
        
        # Set up response listener
        page.on("response", handle_response)
    
    async def _process_response(self, response, step: ApiStep) -> None:
        """Process a single API response."""
        try:
            # Get response body based on type
            if step.response_type == "json":
                try:
                    body = await response.json()
                except:
                    body = await response.text()
            elif step.response_type == "xml":
                body = await response.text()
            else:
                body = await response.text()
            
            # Store the intercepted request data
            request_data = {
                "url": response.url,
                "method": response.request.method,
                "status": response.status,
                "headers": dict(response.headers),
                "body": body,
                "timestamp": response.request.timing
            }
            
            self.intercepted_requests.append(request_data)
            
        except Exception as e:
            self.logger.warning(f"Failed to process API response: {e}")
    
    def _matches_endpoint_pattern(self, url: str, pattern: Optional[str]) -> bool:
        """Check if URL matches the endpoint pattern."""
        if not pattern:
            # If no pattern specified, match common API patterns
            api_patterns = [
                r'/api/',
                r'/rest/',
                r'/v\d+/',
                r'\.json',
                r'/graphql',
                r'/ajax/'
            ]
            return any(re.search(p, url, re.IGNORECASE) for p in api_patterns)
        
        # Use regex pattern matching
        try:
            return bool(re.search(pattern, url, re.IGNORECASE))
        except re.error:
            # If regex is invalid, try simple string matching
            return pattern.lower() in url.lower()
    
    def _wait_for_api_calls(self, page: Any, step: ApiStep) -> None:
        """Wait for API calls to be made."""
        # Wait for network idle to ensure all initial requests are captured
        try:
            page.wait_for_load_state("networkidle", timeout=step.timeout)
        except Exception:
            # If timeout occurs, continue with whatever we have
            pass
        
        # Give a bit more time for async requests
        import time
        time.sleep(1)
    
    def _process_intercepted_requests(self, step: ApiStep) -> List[Dict]:
        """Process all intercepted API requests."""
        results = []
        
        for request_data in self.intercepted_requests:
            try:
                # Extract data from the response body
                extracted_data = self._extract_data_from_response(
                    request_data["body"], step
                )
                
                if extracted_data:
                    # Add metadata
                    result = {
                        "url": request_data["url"],
                        "method": request_data["method"],
                        "status": request_data["status"],
                        "data": extracted_data
                    }
                    
                    # Add name if specified
                    if step.name:
                        result["source"] = step.name
                    
                    results.append(result)
                    
            except Exception as e:
                self.logger.warning(f"Failed to process request data: {e}")
                continue
        
        return results
    
    def _extract_data_from_response(self, body: Any, step: ApiStep) -> Optional[Dict]:
        """Extract data from API response body."""
        if not body:
            return None
        
        try:
            # Handle JSON responses
            if step.response_type == "json" and isinstance(body, (dict, list)):
                data = body
            elif isinstance(body, str):
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    # If not JSON, return as text
                    return {"text": body} if body.strip() else None
            else:
                data = body
            
            # Apply JSONPath if specified
            if step.json_path and isinstance(data, (dict, list)):
                data = self._apply_json_path(data, step.json_path)
                if data is None:
                    return None
            
            # Extract specific fields if specified
            if step.fields:
                if isinstance(data, dict):
                    filtered_data = {}
                    for field in step.fields:
                        if field in data:
                            filtered_data[field] = data[field]
                    return filtered_data if filtered_data else None
                elif isinstance(data, list):
                    # Apply field filtering to each item in the list
                    filtered_list = []
                    for item in data:
                        if isinstance(item, dict):
                            filtered_item = {}
                            for field in step.fields:
                                if field in item:
                                    filtered_item[field] = item[field]
                            if filtered_item:
                                filtered_list.append(filtered_item)
                    return filtered_list if filtered_list else None
            
            return data
            
        except Exception as e:
            self.logger.warning(f"Failed to extract data from response: {e}")
            return None
    
    def _apply_json_path(self, data: Any, json_path: str) -> Any:
        """Apply JSONPath expression to extract specific data."""
        # Simple JSONPath implementation
        # For more complex paths, consider using jsonpath-ng library
        
        try:
            # Handle simple dot notation paths like "data.items"
            if json_path.startswith("$."):
                json_path = json_path[2:]  # Remove $. prefix
            elif json_path.startswith("."):
                json_path = json_path[1:]  # Remove . prefix
            
            parts = json_path.split(".")
            result = data
            
            for part in parts:
                if part:  # Skip empty parts
                    # Handle array indices like "items[0]"
                    if "[" in part and part.endswith("]"):
                        field, index_part = part.split("[", 1)
                        index = int(index_part.rstrip("]"))
                        
                        if field:
                            result = result[field]
                        
                        if isinstance(result, list) and 0 <= index < len(result):
                            result = result[index]
                        else:
                            return None
                    else:
                        # Simple field access
                        if isinstance(result, dict) and part in result:
                            result = result[part]
                        else:
                            return None
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Failed to apply JSONPath '{json_path}': {e}")
            return data


# Example usage queries
API_EXAMPLES = {
    "product_api": {
        "@url": "https://shop.example.com/products/123",
        "@steps": [
            {
                "@api": {
                    "@endpoint": r"/api/products/\d+",
                    "@method": "GET",
                    "@response-type": "json",
                    "@fields": ["id", "name", "price", "availability", "images"]
                },
                "@name": "product_data"
            }
        ]
    },
    
    "search_results": {
        "@url": "https://api-site.com/search?q=laptops",
        "@steps": [
            {
                "@api": {
                    "@endpoint": "/api/search",
                    "@method": "GET", 
                    "@response-type": "json",
                    "@json-path": "$.data.results",
                    "@fields": ["title", "price", "rating", "url"]
                },
                "@name": "search_results"
            }
        ]
    },
    
    "user_profile": {
        "@url": "https://social-site.com/profile/123",
        "@steps": [
            {
                "@api": {
                    "@endpoint": r"/api/users/\d+",
                    "@method": "GET",
                    "@response-type": "json", 
                    "@fields": ["username", "bio", "followers", "following", "posts"]
                },
                "@name": "profile_data"
            }
        ]
    },
    
    "all_apis": {
        "@url": "https://dynamic-site.com",
        "@steps": [
            {
                "@api": {
                    "@response-type": "json"
                },
                "@name": "all_api_data"
            }
        ]
    }
}