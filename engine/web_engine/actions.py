"""
Action execution system for DR Web Engine.
Handles browser interactions like clicking, scrolling, and waiting.
"""

import logging
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .models import Action, ClickAction, ScrollAction, WaitAction, FillAction, HoverAction, JavaScriptAction

logger = logging.getLogger(__name__)


class ActionHandler(ABC):
    """Abstract base class for action handlers."""
    
    @abstractmethod
    def can_handle(self, action: Action) -> bool:
        """Check if this handler can process the given action."""
        pass
    
    @abstractmethod
    def execute(self, page: Any, action: Action) -> None:
        """Execute the action on the given page."""
        pass


class ClickActionHandler(ActionHandler):
    """Handles click actions."""
    
    def can_handle(self, action: Action) -> bool:
        return isinstance(action, ClickAction)
    
    def execute(self, page: Any, action: ClickAction) -> None:
        """Execute a click action."""
        try:
            if action.xpath:
                # Use XPath selector
                element = page.query_selector(f"xpath={action.xpath}")
                if element:
                    element.click()
                    logger.info(f"Clicked element with XPath: {action.xpath}")
                else:
                    logger.warning(f"Element not found with XPath: {action.xpath}")
            elif action.selector:
                # Use CSS selector
                element = page.query_selector(action.selector)
                if element:
                    element.click()
                    logger.info(f"Clicked element with selector: {action.selector}")
                else:
                    logger.warning(f"Element not found with selector: {action.selector}")
        except Exception as e:
            logger.error(f"Failed to click element: {e}")


class ScrollActionHandler(ActionHandler):
    """Handles scroll actions."""
    
    def can_handle(self, action: Action) -> bool:
        return isinstance(action, ScrollAction)
    
    def execute(self, page: Any, action: ScrollAction) -> None:
        """Execute a scroll action."""
        try:
            if action.selector:
                # Scroll to specific element
                element = page.query_selector(action.selector)
                if element:
                    element.scroll_into_view_if_needed()
                    logger.info(f"Scrolled to element: {action.selector}")
                else:
                    logger.warning(f"Element not found for scrolling: {action.selector}")
            elif action.pixels:
                # Scroll by pixels
                direction_map = {
                    "down": (0, action.pixels),
                    "up": (0, -action.pixels),
                    "right": (action.pixels, 0),
                    "left": (-action.pixels, 0)
                }
                delta_x, delta_y = direction_map.get(action.direction, (0, action.pixels))
                
                # Use JavaScript to scroll
                page.evaluate(f"window.scrollBy({delta_x}, {delta_y})")
                logger.info(f"Scrolled {action.direction} by {action.pixels} pixels")
            else:
                # Default scroll down by viewport height
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                logger.info(f"Scrolled {action.direction} by viewport height")
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")


class WaitActionHandler(ActionHandler):
    """Handles wait actions."""
    
    def can_handle(self, action: Action) -> bool:
        return isinstance(action, WaitAction)
    
    def execute(self, page: Any, action: WaitAction) -> None:
        """Execute a wait action."""
        try:
            if action.until == "element":
                # Wait for element to appear
                selector = action.xpath if action.xpath else action.selector
                if selector:
                    if action.xpath:
                        page.wait_for_selector(f"xpath={action.xpath}", timeout=action.timeout)
                        logger.info(f"Waited for element with XPath: {action.xpath}")
                    else:
                        page.wait_for_selector(action.selector, timeout=action.timeout)
                        logger.info(f"Waited for element: {action.selector}")
                else:
                    logger.warning("No selector provided for element wait")
                    
            elif action.until == "text":
                # Wait for text to appear
                if action.text and (action.selector or action.xpath):
                    selector = action.xpath if action.xpath else action.selector
                    if action.xpath:
                        page.wait_for_function(
                            f"""() => {{
                                const element = document.evaluate('{action.xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                return element && element.textContent.includes('{action.text}');
                            }}""",
                            timeout=action.timeout
                        )
                    else:
                        page.wait_for_function(
                            f"() => document.querySelector('{action.selector}')?.textContent?.includes('{action.text}')",
                            timeout=action.timeout
                        )
                    logger.info(f"Waited for text '{action.text}' to appear")
                else:
                    logger.warning("Text and selector required for text wait")
                    
            elif action.until == "network-idle":
                # Wait for network to be idle
                page.wait_for_load_state("networkidle", timeout=action.timeout)
                logger.info("Waited for network idle")
                
            elif action.until == "timeout":
                # Simple timeout wait
                page.wait_for_timeout(action.timeout)
                logger.info(f"Waited for {action.timeout}ms")
                
        except Exception as e:
            logger.error(f"Failed to wait: {e}")


class FillActionHandler(ActionHandler):
    """Handles form fill actions."""
    
    def can_handle(self, action: Action) -> bool:
        return isinstance(action, FillAction)
    
    def execute(self, page: Any, action: FillAction) -> None:
        """Execute a fill action."""
        try:
            if action.xpath:
                element = page.query_selector(f"xpath={action.xpath}")
                if element:
                    element.fill(action.value)
                    logger.info(f"Filled element with XPath: {action.xpath}")
                else:
                    logger.warning(f"Element not found with XPath: {action.xpath}")
            elif action.selector:
                element = page.query_selector(action.selector)
                if element:
                    element.fill(action.value)
                    logger.info(f"Filled element with selector: {action.selector}")
                else:
                    logger.warning(f"Element not found with selector: {action.selector}")
        except Exception as e:
            logger.error(f"Failed to fill element: {e}")


class HoverActionHandler(ActionHandler):
    """Handles hover actions."""
    
    def can_handle(self, action: Action) -> bool:
        return isinstance(action, HoverAction)
    
    def execute(self, page: Any, action: HoverAction) -> None:
        """Execute a hover action."""
        try:
            if action.xpath:
                element = page.query_selector(f"xpath={action.xpath}")
                if element:
                    element.hover()
                    logger.info(f"Hovered over element with XPath: {action.xpath}")
                else:
                    logger.warning(f"Element not found with XPath: {action.xpath}")
            elif action.selector:
                element = page.query_selector(action.selector)
                if element:
                    element.hover()
                    logger.info(f"Hovered over element with selector: {action.selector}")
                else:
                    logger.warning(f"Element not found with selector: {action.selector}")
        except Exception as e:
            logger.error(f"Failed to hover over element: {e}")


class JavaScriptActionHandler(ActionHandler):
    """Handles JavaScript execution actions."""
    
    def can_handle(self, action: Action) -> bool:
        return isinstance(action, JavaScriptAction)
    
    def execute(self, page: Any, action: JavaScriptAction) -> Any:
        """Execute JavaScript code and optionally return the result."""
        try:
            logger.info(f"Executing JavaScript: {action.code[:100]}...")
            
            # Execute the JavaScript code
            result = page.evaluate(action.code)
            
            # If there's a wait condition, wait for it
            if action.wait_for:
                logger.info(f"Waiting for condition: {action.wait_for}")
                try:
                    page.wait_for_function(action.wait_for, timeout=action.timeout)
                    logger.info("Wait condition satisfied")
                except Exception as wait_error:
                    logger.warning(f"Wait condition failed: {wait_error}")
            
            # Log the result if any
            if result is not None:
                logger.info(f"JavaScript execution returned: {str(result)[:200]}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            return None


class ActionProcessor:
    """Main processor for executing actions."""
    
    def __init__(self):
        self.handlers = [
            ClickActionHandler(),
            ScrollActionHandler(),
            WaitActionHandler(),
            FillActionHandler(),
            HoverActionHandler(),
            JavaScriptActionHandler()
        ]
    
    def execute_action(self, page: Any, action: Action) -> None:
        """Execute a single action using appropriate handler."""
        for handler in self.handlers:
            if handler.can_handle(action):
                handler.execute(page, action)
                return
        
        logger.warning(f"No handler found for action type: {type(action)}")
    
    def execute_actions(self, page: Any, actions: list[Action]) -> None:
        """Execute a list of actions in sequence."""
        if not actions:
            return
            
        logger.info(f"Executing {len(actions)} actions")
        for i, action in enumerate(actions):
            logger.debug(f"Executing action {i+1}/{len(actions)}: {action.type}")
            self.execute_action(page, action)