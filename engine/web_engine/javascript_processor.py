"""
JavaScript step processor for executing JavaScript code in data extraction steps.
"""

import logging
import json
from typing import Any, List

from .processors import StepProcessor
from .models import JavaScriptStep

logger = logging.getLogger(__name__)


class JavaScriptStepProcessor(StepProcessor):
    """Processes JavaScriptStep instances for JavaScript-based data extraction."""
    
    def __init__(self):
        super().__init__()
        self.priority = 20  # Higher precedence than most other processors
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is a JavaScriptStep."""
        return isinstance(step, JavaScriptStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return ["JavaScriptStep"]
    
    def execute(self, context: Any, page: Any, step: JavaScriptStep) -> List[Any]:
        """Execute JavaScript code for data extraction."""
        try:
            self.logger.info(f"Executing JavaScript step: {step.code[:100]}...")
            
            # Execute the JavaScript code
            result = page.evaluate(step.code, timeout=step.timeout)
            
            # Handle the result
            if result is None:
                self.logger.warning("JavaScript execution returned no result")
                return []
            
            # Parse JSON if requested and result is a string
            if step.return_json and isinstance(result, str):
                try:
                    result = json.loads(result)
                    self.logger.debug("Successfully parsed JavaScript result as JSON")
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse JavaScript result as JSON: {e}")
                    # Continue with the raw string result
            
            # Ensure result is in list format
            if isinstance(result, list):
                processed_results = result
            elif isinstance(result, dict):
                processed_results = [result]
            else:
                # For primitive values, wrap in a dict with step name or default key
                key = step.name or 'javascript_result'
                processed_results = [{key: result}]
            
            self.logger.info(f"JavaScript step returned {len(processed_results)} result(s)")
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Failed to execute JavaScript step: {e}")
            return []


class JavaScriptContext:
    """Helper class to provide common JavaScript utilities."""
    
    @staticmethod
    def get_common_utilities() -> str:
        """Return common JavaScript utility functions."""
        return """
        // Utility functions for DR Web Engine JavaScript execution
        
        // Extract text content from elements
        function extractText(selector) {
            const elements = document.querySelectorAll(selector);
            return Array.from(elements).map(el => el.textContent.trim());
        }
        
        // Extract attribute values
        function extractAttribute(selector, attribute) {
            const elements = document.querySelectorAll(selector);
            return Array.from(elements).map(el => el.getAttribute(attribute));
        }
        
        // Extract structured data from elements
        function extractData(selector, fields) {
            const elements = document.querySelectorAll(selector);
            return Array.from(elements).map(el => {
                const result = {};
                for (const [key, fieldSelector] of Object.entries(fields)) {
                    const fieldElement = el.querySelector(fieldSelector);
                    result[key] = fieldElement ? fieldElement.textContent.trim() : null;
                }
                return result;
            });
        }
        
        // Wait for elements to appear
        function waitForElements(selector, maxWait = 5000) {
            return new Promise((resolve, reject) => {
                const startTime = Date.now();
                function check() {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        resolve(elements);
                    } else if (Date.now() - startTime > maxWait) {
                        reject(new Error('Elements not found within timeout'));
                    } else {
                        setTimeout(check, 100);
                    }
                }
                check();
            });
        }
        
        // Scroll and load more content
        function scrollAndWait(pixels = 500, waitTime = 2000) {
            window.scrollBy(0, pixels);
            return new Promise(resolve => setTimeout(resolve, waitTime));
        }
        """
    
    @staticmethod
    def wrap_code_with_utilities(code: str) -> str:
        """Wrap user code with utility functions."""
        utilities = JavaScriptContext.get_common_utilities()
        return f"{utilities}\n\n// User code:\n{code}"