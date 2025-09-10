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
        self.extractor = XPathExtractor()
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is an ExtractStep."""
        return isinstance(step, ExtractStep)
    
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
                link = self.extractor.extract_value(element, step.follow.xpath, base_url=page.url)

                if link:
                    self.logger.info(f"Following link: {link}")

                    with context.new_page() as new_page:
                        new_page.goto(link)
                        new_page.wait_for_load_state("domcontentloaded")

                        for follow_step in step.follow.steps:
                            # Import here to avoid circular imports
                            from .engine import execute_step
                            follow_results = execute_step(context, new_page, follow_step)

                            if isinstance(follow_results, dict) and follow_results:
                                item.update(follow_results)
                            elif isinstance(follow_results, list) and follow_results:
                                structured_list = [result for result in follow_results if isinstance(result, dict)]
                                if structured_list:
                                    key = follow_step.name or follow_step.xpath
                                    item.setdefault(key, []).extend(structured_list)

            results.append(item)

        return results if results else []