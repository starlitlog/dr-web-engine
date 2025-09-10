"""
Enhanced FollowStep processor with recursive navigation support.
Handles Kleene star patterns, cycle detection, and depth control.
"""

import logging
from typing import Any, Dict, List, Set
from urllib.parse import urljoin, urlparse

from .processors import StepProcessor
from .models import FollowStep, ExtractStep, ConditionalStep
from .extractor import XPathExtractor

logger = logging.getLogger(__name__)


class FollowStepProcessor(StepProcessor):
    """Processes FollowStep instances with enhanced recursive navigation."""
    
    def __init__(self):
        super().__init__()
        self.priority = 30  # Higher precedence than Extract and Conditional
        self.extractor = XPathExtractor()
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is a FollowStep."""
        return isinstance(step, FollowStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return ["FollowStep"]
    
    def execute(self, context: Any, page: Any, step: FollowStep) -> List[Any]:
        """Execute enhanced link following with cycle detection and depth control."""
        results = []
        visited_urls: Set[str] = set()
        
        # Start navigation from current page
        self._navigate_recursive(
            context, page, step, results, visited_urls, 
            current_depth=0, base_url=page.url
        )
        
        return results
    
    def _navigate_recursive(self, context: Any, page: Any, follow_step: FollowStep, 
                          results: List[Any], visited_urls: Set[str], 
                          current_depth: int, base_url: str) -> None:
        """Recursively navigate links with depth and cycle control."""
        
        # Check depth limit
        if follow_step.max_depth and current_depth >= follow_step.max_depth:
            self.logger.debug(f"Max depth {follow_step.max_depth} reached, stopping navigation")
            return
        
        # Extract links from current page
        links = self._extract_links(page, follow_step.xpath, base_url)
        self.logger.debug(f"Found {len(links)} links at depth {current_depth}")
        
        for link in links:
            # Cycle detection
            if follow_step.detect_cycles and link in visited_urls:
                self.logger.debug(f"Cycle detected for {link}, skipping")
                continue
            
            # External link filtering
            if not follow_step.follow_external and self._is_external_link(link, base_url):
                self.logger.debug(f"External link {link} skipped")
                continue
            
            # Mark as visited
            if follow_step.detect_cycles:
                visited_urls.add(link)
            
            try:
                # Navigate to the new page
                self.logger.info(f"Following link: {link} (depth: {current_depth + 1})")
                
                with context.new_page() as new_page:
                    new_page.goto(link)
                    new_page.wait_for_load_state("domcontentloaded")
                    
                    # Execute steps on the new page
                    page_results = self._execute_steps_on_page(context, new_page, follow_step.steps)
                    results.extend(page_results)
                    
                    # Look for more links to follow (recursive step)
                    self._navigate_recursive(
                        context, new_page, follow_step, results, visited_urls,
                        current_depth + 1, base_url
                    )
                        
            except Exception as e:
                self.logger.error(f"Error following link {link}: {e}")
                continue
            
            finally:
                # Remove from visited set if we're backtracking (allows revisiting in different paths)
                if follow_step.detect_cycles and current_depth > 0:
                    visited_urls.discard(link)
    
    def _extract_links(self, page: Any, xpath: str, base_url: str) -> List[str]:
        """Extract and normalize links from page."""
        links = []
        
        try:
            elements = page.query_selector_all(f"xpath={xpath}")
            
            for element in elements:
                link = self.extractor.extract_value(element, ".", base_url=base_url)
                if link and self._is_valid_url(link):
                    links.append(link)
                    
        except Exception as e:
            self.logger.error(f"Error extracting links with XPath {xpath}: {e}")
        
        return links
    
    def _execute_steps_on_page(self, context: Any, page: Any, steps: List[Any]) -> List[Any]:
        """Execute steps on a followed page."""
        results = []
        
        # Import registry here to avoid circular imports
        from .processors import StepProcessorRegistry
        from .extract_processor import ExtractStepProcessor
        from .conditionals import ConditionalProcessor
        
        # Create a temporary registry for this execution
        registry = StepProcessorRegistry()
        registry.register(ExtractStepProcessor())
        registry.register(ConditionalProcessor())
        registry.register(FollowStepProcessor())  # Support nested follows
        
        for step in steps:
            try:
                step_results = registry.process_step(context, page, step)
                if isinstance(step_results, list):
                    results.extend(step_results)
                elif isinstance(step_results, dict) and step_results:
                    results.append(step_results)
                    
            except Exception as e:
                self.logger.error(f"Error executing step on followed page: {e}")
                continue
        
        return results
    
    def _is_external_link(self, link: str, base_url: str) -> bool:
        """Check if link is external to the base domain."""
        try:
            link_domain = urlparse(link).netloc
            base_domain = urlparse(base_url).netloc
            return link_domain != base_domain and link_domain != ""
        except Exception:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme in ('http', 'https') and parsed.netloc)
        except Exception:
            return False