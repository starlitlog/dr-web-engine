"""
Step Processor System for DR Web Engine.
Provides modular, extensible architecture for processing different step types.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .models import Step

logger = logging.getLogger(__name__)


class StepProcessor(ABC):
    """Abstract base class for step processors."""
    
    def __init__(self):
        self.logger = logger
    
    @abstractmethod
    def can_handle(self, step: Step) -> bool:
        """Check if this processor can handle the given step type."""
        pass
    
    @abstractmethod
    def execute(self, context: Any, page: Any, step: Step) -> List[Any]:
        """Execute the step and return results."""
        pass


class StepProcessorRegistry:
    """Registry for managing step processors."""
    
    def __init__(self):
        self.processors: List[StepProcessor] = []
        self.logger = logger
    
    def register(self, processor: StepProcessor) -> None:
        """Register a new step processor."""
        self.processors.append(processor)
        self.logger.debug(f"Registered processor: {processor.__class__.__name__}")
    
    def find_processor(self, step: Step) -> Optional[StepProcessor]:
        """Find the first processor that can handle the given step."""
        for processor in self.processors:
            if processor.can_handle(step):
                return processor
        return None
    
    def process_step(self, context: Any, page: Any, step: Step) -> List[Any]:
        """Process a step using the appropriate processor."""
        processor = self.find_processor(step)
        if processor:
            self.logger.debug(f"Processing {type(step).__name__} with {processor.__class__.__name__}")
            return processor.execute(context, page, step)
        else:
            self.logger.warning(f"No processor found for step type: {type(step).__name__}")
            return []