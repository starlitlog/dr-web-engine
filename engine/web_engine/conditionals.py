"""
Conditional logic system for DR Web Engine.
Handles condition evaluation and branching execution.
"""

import logging
from typing import Any, List
from abc import ABC, abstractmethod

from .models import ConditionSpec, ConditionalStep, Step, ExtractStep
from .processors import StepProcessor

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates conditions against page content"""
    
    def __init__(self):
        self.logger = logger
    
    def evaluate(self, page: Any, condition: ConditionSpec) -> bool:
        """Evaluate a condition against the current page"""
        try:
            # Element existence checks
            if condition.exists:
                result = self._check_exists(page, condition.exists)
                self.logger.debug(f"Condition '@exists {condition.exists}' = {result}")
                return result
                
            if condition.not_exists:
                result = not self._check_exists(page, condition.not_exists)
                self.logger.debug(f"Condition '@not-exists {condition.not_exists}' = {result}")
                return result
            
            # Text content checks
            if condition.contains:
                result = self._check_contains(page, condition)
                self.logger.debug(f"Condition '@contains {condition.contains}' = {result}")
                return result
            
            # Element count checks
            if condition.count is not None:
                result = self._check_count(page, condition, exact=condition.count)
                self.logger.debug(f"Condition '@count {condition.count}' = {result}")
                return result
                
            if condition.min_count is not None:
                result = self._check_count(page, condition, min_count=condition.min_count)
                self.logger.debug(f"Condition '@min-count {condition.min_count}' = {result}")
                return result
                
            if condition.max_count is not None:
                result = self._check_count(page, condition, max_count=condition.max_count)
                self.logger.debug(f"Condition '@max-count {condition.max_count}' = {result}")
                return result
            
            # If no conditions specified, default to False
            self.logger.warning("No condition specified, defaulting to False")
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _check_exists(self, page: Any, selector: str) -> bool:
        """Check if element exists on page"""
        try:
            if selector.startswith("//"):
                # XPath selector
                element = page.query_selector(f"xpath={selector}")
            else:
                # CSS selector
                element = page.query_selector(selector)
            return element is not None
        except Exception as e:
            self.logger.error(f"Error checking element existence for '{selector}': {e}")
            return False
    
    def _check_contains(self, page: Any, condition: ConditionSpec) -> bool:
        """Check if element contains specific text"""
        try:
            selector = condition.xpath if condition.xpath else condition.selector
            if not selector:
                # Check page text content
                content = page.text_content() or ""
                return condition.contains in content
            
            if selector.startswith("//"):
                # XPath selector
                element = page.query_selector(f"xpath={selector}")
            else:
                # CSS selector  
                element = page.query_selector(selector)
            
            if element:
                text_content = element.text_content() or ""
                return condition.contains in text_content
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking text content: {e}")
            return False
    
    def _check_count(self, page: Any, condition: ConditionSpec, exact: int = None, 
                    min_count: int = None, max_count: int = None) -> bool:
        """Check element count conditions"""
        try:
            selector = condition.xpath if condition.xpath else condition.selector
            if not selector:
                self.logger.warning("No selector provided for count check")
                return False
            
            if selector.startswith("//"):
                # XPath selector
                elements = page.query_selector_all(f"xpath={selector}")
            else:
                # CSS selector
                elements = page.query_selector_all(selector)
            
            count = len(elements) if elements else 0
            
            if exact is not None:
                return count == exact
            if min_count is not None and count < min_count:
                return False
            if max_count is not None and count > max_count:
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error checking element count: {e}")
            return False


class ConditionalProcessor(StepProcessor):
    """Processes conditional steps in extraction queries"""
    
    def __init__(self):
        super().__init__()
        self.priority = 40  # Higher precedence than ExtractStep
        self.evaluator = ConditionEvaluator()
    
    def can_handle(self, step: Any) -> bool:
        """Check if this processor can handle the given step type."""
        return isinstance(step, ConditionalStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return ["ConditionalStep"]
    
    def execute(self, context: Any, page: Any, step: ConditionalStep) -> List[Any]:
        """Execute the conditional step using the standard processor interface."""
        return self.process_conditional(page, step)
    
    def process_conditional(self, page: Any, conditional: ConditionalStep) -> List[Any]:
        """Process a conditional step and return results from executed branch"""
        self.logger.info(f"Processing conditional step")
        
        # Evaluate the condition
        condition_result = self.evaluator.evaluate(page, conditional.condition)
        
        if condition_result:
            self.logger.info("Condition evaluated to True, executing @then branch")
            return self._execute_steps(page, conditional.then_steps)
        else:
            self.logger.info("Condition evaluated to False, executing @else branch")
            if conditional.else_steps:
                return self._execute_steps(page, conditional.else_steps)
            else:
                self.logger.info("No @else branch defined, skipping")
                return []
    
    def _execute_steps(self, page: Any, steps: List[Step]) -> List[Any]:
        """Execute a list of steps (recursive for nested conditionals)"""
        results = []
        
        for step in steps:
            if isinstance(step, ConditionalStep):
                # Recursive conditional processing
                conditional_results = self.process_conditional(page, step)
                results.extend(conditional_results)
            elif isinstance(step, ExtractStep):
                # Import here to avoid circular import
                from .engine import execute_step
                from .base.browser import BrowserClient
                
                # For now, create a simple context for extraction
                # TODO: This should be improved to use proper context management
                context = page.context
                step_results = execute_step(context, page, step)
                if isinstance(step_results, list):
                    results.extend(step_results)
                elif isinstance(step_results, dict) and step_results:
                    results.append(step_results)
            else:
                self.logger.warning(f"Unknown step type: {type(step)}")
        
        return results
    
    def can_handle(self, step: Any) -> bool:
        """Check if this processor can handle the given step"""
        return isinstance(step, ConditionalStep)