"""
Smart Retry Plugin Implementation
Adds intelligent retry logic to any step with configurable backoff strategies.
"""

import time
import random
import logging
from typing import List, Dict, Any, Optional
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor
from engine.web_engine.models import BaseModel
from pydantic import Field

logger = logging.getLogger(__name__)


class SmartRetryStep(BaseModel):
    """Smart retry configuration step."""
    max_attempts: int = Field(default=3, alias="@max-attempts", ge=1, le=10)
    backoff_strategy: str = Field(default="exponential", alias="@backoff", pattern="^(linear|exponential|fixed)$")
    base_delay: int = Field(default=1000, alias="@base-delay", ge=100, le=60000)  # milliseconds
    max_delay: int = Field(default=30000, alias="@max-delay", ge=1000, le=300000)  # milliseconds
    retry_on_errors: List[str] = Field(default_factory=lambda: ["timeout", "network", "5xx"], alias="@retry-on")
    jitter: bool = Field(default=True, alias="@jitter")  # Add randomization to prevent thundering herd
    target_step: Dict[str, Any] = Field(alias="@step")  # The step to retry


class SmartRetryProcessor(StepProcessor):
    """
    Smart retry processor with configurable backoff strategies.
    
    Supports:
    - Exponential, linear, and fixed backoff
    - Jitter to prevent thundering herd
    - Conditional retry based on error types
    - Detailed retry metrics and logging
    """
    
    def __init__(self):
        super().__init__()
        self.priority = 10  # Very high priority - should wrap other steps
        self.retry_metrics = {}
    
    def can_handle(self, step: Any) -> bool:
        return isinstance(step, SmartRetryStep)
    
    def get_supported_step_types(self) -> List[str]:
        return ["SmartRetryStep"]
    
    def execute(self, context: Any, page: Any, step: SmartRetryStep) -> List[Any]:
        """Execute step with smart retry logic."""
        attempt = 0
        last_error = None
        
        while attempt < step.max_attempts:
            try:
                attempt += 1
                self.logger.info(f"Retry attempt {attempt}/{step.max_attempts}")
                
                # Execute the target step
                # Note: This is a simplified implementation - in reality we'd need
                # to properly resolve and execute the target step through the registry
                results = self._execute_target_step(context, page, step.target_step)
                
                # Success - log metrics and return
                self._log_success_metrics(step, attempt)
                return results
                
            except Exception as e:
                last_error = e
                error_type = self._classify_error(e)
                
                self.logger.warning(f"Attempt {attempt} failed: {error_type} - {str(e)}")
                
                # Check if we should retry this error type
                if not self._should_retry_error(error_type, step.retry_on_errors):
                    self.logger.info(f"Error type '{error_type}' not in retry list, giving up")
                    break
                
                # Don't sleep on the last attempt
                if attempt < step.max_attempts:
                    delay = self._calculate_delay(step, attempt)
                    self.logger.info(f"Retrying in {delay}ms...")
                    time.sleep(delay / 1000.0)
        
        # All attempts failed
        self._log_failure_metrics(step, attempt, last_error)
        self.logger.error(f"All {step.max_attempts} attempts failed. Last error: {last_error}")
        return []  # Return empty results instead of propagating error
    
    def _execute_target_step(self, context: Any, page: Any, target_step: Dict[str, Any]) -> List[Any]:
        """Execute the target step that we're retrying."""
        from engine.web_engine.models import parse_step
        from engine.web_engine.processors import get_default_registry
        
        try:
            # Parse the step dictionary into a proper Step object
            step_obj = parse_step(target_step)
            
            # Get the processor registry
            registry = get_default_registry()
            
            # Find the appropriate processor
            processor = registry.find_processor(step_obj)
            
            if processor:
                # Execute the step through the processor
                return processor.execute(context, page, step_obj)
            else:
                self.logger.error(f"No processor found for step type: {type(step_obj).__name__}")
                return []
                
        except Exception as e:
            # Re-raise the exception to trigger retry logic
            raise
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for retry decision."""
        error_str = str(error).lower()
        
        if isinstance(error, TimeoutError) or "timeout" in error_str:
            return "timeout"
        elif isinstance(error, ConnectionError) or "connection" in error_str or "network" in error_str:
            return "network"
        elif "502" in error_str or "503" in error_str or "504" in error_str:
            return "5xx"
        elif "500" in error_str:
            return "server-error"
        elif "404" in error_str:
            return "not-found"
        elif "403" in error_str or "401" in error_str:
            return "auth"
        else:
            return "unknown"
    
    def _should_retry_error(self, error_type: str, retry_on_errors: List[str]) -> bool:
        """Check if this error type should trigger a retry."""
        return error_type in retry_on_errors
    
    def _calculate_delay(self, step: SmartRetryStep, attempt: int) -> int:
        """Calculate delay for next retry attempt."""
        if step.backoff_strategy == "fixed":
            delay = step.base_delay
        elif step.backoff_strategy == "linear":
            delay = step.base_delay * attempt
        elif step.backoff_strategy == "exponential":
            delay = step.base_delay * (2 ** (attempt - 1))
        else:
            delay = step.base_delay
        
        # Cap at max_delay
        delay = min(delay, step.max_delay)
        
        # Add jitter to prevent thundering herd
        if step.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            delay = int(delay + jitter)
        
        return max(delay, 100)  # Minimum 100ms delay
    
    def _log_success_metrics(self, step: SmartRetryStep, attempts_used: int):
        """Log successful retry metrics."""
        metric_key = f"{step.backoff_strategy}_{step.max_attempts}"
        if metric_key not in self.retry_metrics:
            self.retry_metrics[metric_key] = {"successes": 0, "failures": 0, "total_attempts": 0}
        
        self.retry_metrics[metric_key]["successes"] += 1
        self.retry_metrics[metric_key]["total_attempts"] += attempts_used
        
        self.logger.info(f"Retry succeeded after {attempts_used} attempts")
    
    def _log_failure_metrics(self, step: SmartRetryStep, attempts_used: int, error: Exception):
        """Log failed retry metrics."""
        metric_key = f"{step.backoff_strategy}_{step.max_attempts}"
        if metric_key not in self.retry_metrics:
            self.retry_metrics[metric_key] = {"successes": 0, "failures": 0, "total_attempts": 0}
        
        self.retry_metrics[metric_key]["failures"] += 1
        self.retry_metrics[metric_key]["total_attempts"] += attempts_used
        
        error_type = self._classify_error(error)
        self.logger.error(f"Retry failed after {attempts_used} attempts. Error type: {error_type}")
    
    def get_retry_metrics(self) -> Dict[str, Dict[str, int]]:
        """Get retry performance metrics."""
        return self.retry_metrics.copy()


class SmartRetryPlugin(DrWebPlugin):
    """
    Smart Retry plugin for intelligent retry logic.
    
    Provides exponential backoff, jitter, and configurable retry conditions
    to improve extraction reliability and reduce failures.
    """
    
    def __init__(self):
        self._processor = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="smart-retry",
            version="1.0.0",
            description="Intelligent retry logic with exponential backoff and custom error handling",
            author="DR Web Engine Team",
            homepage="https://github.com/starlitlog/dr-web-engine",
            supported_step_types=["SmartRetryStep"],
            dependencies=[],
            min_drweb_version="0.10.0",
            enabled=True
        )
    
    def get_processors(self) -> List[StepProcessor]:
        if not self._processor:
            self._processor = SmartRetryProcessor()
        return [self._processor]
    
    def get_retry_metrics(self) -> Dict[str, Dict[str, int]]:
        """Get retry performance metrics from the processor."""
        if self._processor:
            return self._processor.get_retry_metrics()
        return {}
    
    def finalize(self) -> None:
        if self._processor:
            # Log final metrics
            metrics = self._processor.get_retry_metrics()
            if metrics:
                logger.info(f"Smart Retry final metrics: {metrics}")
        self._processor = None