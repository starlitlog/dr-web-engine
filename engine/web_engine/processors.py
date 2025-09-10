"""
Step Processor System for DR Web Engine.
Provides modular, extensible architecture for processing different step types.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import Step

logger = logging.getLogger(__name__)


class StepProcessor(ABC):
    """Abstract base class for step processors."""
    
    def __init__(self):
        self.logger = logger
        self.name = self.__class__.__name__
        self.priority = 100  # Default priority, lower = higher priority
    
    @abstractmethod
    def can_handle(self, step: Step) -> bool:
        """Check if this processor can handle the given step type."""
        pass
    
    @abstractmethod
    def execute(self, context: Any, page: Any, step: Step) -> List[Any]:
        """Execute the step and return results."""
        pass
    
    def initialize(self) -> None:
        """Initialize processor (called when registered)."""
        pass
    
    def finalize(self) -> None:
        """Cleanup processor resources (called when unregistered)."""
        pass
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return []


class StepProcessorRegistry:
    """Enhanced registry for managing step processors with plugin support."""
    
    def __init__(self):
        self.processors: List[StepProcessor] = []
        self._processor_map: Dict[str, StepProcessor] = {}
        self.logger = logger
    
    def register(self, processor: StepProcessor) -> None:
        """Register a new step processor with lifecycle management."""
        try:
            # Initialize the processor
            processor.initialize()
            
            # Add to registry sorted by priority
            self.processors.append(processor)
            self.processors.sort(key=lambda p: p.priority)
            
            # Update processor map for fast lookup
            for step_type in processor.get_supported_step_types():
                self._processor_map[step_type] = processor
            
            self.logger.info(f"Registered processor: {processor.name} (priority: {processor.priority})")
            
        except Exception as e:
            self.logger.error(f"Failed to register processor {processor.name}: {e}")
            raise
    
    def unregister(self, processor_name: str) -> bool:
        """Unregister a processor by name."""
        for i, processor in enumerate(self.processors):
            if processor.name == processor_name:
                try:
                    processor.finalize()
                    self.processors.pop(i)
                    
                    # Update processor map
                    for step_type in processor.get_supported_step_types():
                        if self._processor_map.get(step_type) == processor:
                            del self._processor_map[step_type]
                    
                    self.logger.info(f"Unregistered processor: {processor_name}")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Failed to unregister processor {processor_name}: {e}")
                    return False
        
        self.logger.warning(f"Processor not found: {processor_name}")
        return False
    
    def find_processor(self, step: Step) -> Optional[StepProcessor]:
        """Find the best processor that can handle the given step (priority-ordered)."""
        step_type = type(step).__name__
        
        # Fast lookup first
        if step_type in self._processor_map:
            processor = self._processor_map[step_type]
            if processor.can_handle(step):
                return processor
        
        # Fallback to full search (allows for complex can_handle logic)
        for processor in self.processors:
            try:
                if processor.can_handle(step):
                    return processor
            except Exception as e:
                self.logger.error(f"Error in {processor.name}.can_handle(): {e}")
                continue
        
        return None
    
    def process_step(self, context: Any, page: Any, step: Step) -> List[Any]:
        """Process a step using the appropriate processor with error handling."""
        processor = self.find_processor(step)
        if processor:
            try:
                self.logger.debug(f"Processing {type(step).__name__} with {processor.name}")
                return processor.execute(context, page, step)
                
            except Exception as e:
                self.logger.error(f"Error executing step with {processor.name}: {e}")
                # Could implement fallback strategies here
                return []
        else:
            self.logger.warning(f"No processor found for step type: {type(step).__name__}")
            return []
    
    def get_registered_processors(self) -> List[str]:
        """Get list of registered processor names."""
        return [p.name for p in self.processors]
    
    def get_processor_info(self, processor_name: str) -> Optional[dict]:
        """Get detailed information about a processor."""
        for processor in self.processors:
            if processor.name == processor_name:
                return {
                    "name": processor.name,
                    "priority": processor.priority,
                    "supported_types": processor.get_supported_step_types(),
                    "class": processor.__class__.__name__
                }
        return None