"""
ExtractStep processor implementation.
Handles XPath-based data extraction steps.
"""

import logging
from typing import Any, List

from .processors import StepProcessor
from .models import ExtractStep
from .extractor import XPathExtractor

logger = logging.getLogger(__name__)


class ExtractStepProcessor(StepProcessor):
    """Processes ExtractStep instances for XPath-based data extraction."""
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # Lower priority = higher precedence
        self.extractor = XPathExtractor()
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is an ExtractStep."""
        return isinstance(step, ExtractStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return ["ExtractStep"]
    
    def execute(self, context: Any, page: Any, step: ExtractStep) -> List[Any]:
        """Execute XPath extraction logic."""
        results = []

        # Find elements using XPath
        elements = page.query_selector_all(f"xpath={step.xpath}")
        self.logger.debug(f"Found {len(elements)} elements with XPath: {step.xpath}")

        # Extract data from each element
        for element in elements:
            item = self.extractor.extract_fields(element, step.fields)

            # Handle link following if specified
            if step.follow:
                # Use the new FollowStepProcessor for enhanced navigation
                from .follow_processor import FollowStepProcessor
                follow_processor = FollowStepProcessor()
                
                follow_results = follow_processor.execute(context, page, step.follow)
                if follow_results:
                    # Merge follow results with the current item
                    if len(follow_results) == 1 and isinstance(follow_results[0], dict):
                        item.update(follow_results[0])
                    else:
                        # Multiple results or complex structure
                        follow_key = step.follow.xpath.split('/')[-1] or 'followed_data'
                        item[follow_key] = follow_results

            results.append(item)

        return results if results else []