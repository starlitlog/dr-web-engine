"""
Tests for the step processor system and registry.
"""

import pytest
from unittest.mock import MagicMock

from engine.web_engine.processors import StepProcessor, StepProcessorRegistry
from engine.web_engine.models import ExtractStep, ConditionalStep


class MockProcessor(StepProcessor):
    """Mock processor for testing."""
    
    def __init__(self, name="MockProcessor", priority=100, supported_types=None):
        super().__init__()
        self.name = name
        self.priority = priority
        self._supported_types = supported_types or ["TestStep"]
        self.initialized = False
        self.finalized = False
    
    def can_handle(self, step):
        return type(step).__name__ in self._supported_types
    
    def execute(self, context, page, step):
        return [{"mock_result": True}]
    
    def get_supported_step_types(self):
        return self._supported_types
    
    def initialize(self):
        self.initialized = True
    
    def finalize(self):
        self.finalized = True


class TestStepProcessorRegistry:
    
    def test_registry_initialization(self):
        registry = StepProcessorRegistry()
        assert len(registry.processors) == 0
        assert len(registry._processor_map) == 0
        assert registry.get_registered_processors() == []
    
    def test_register_processor(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", priority=50, supported_types=["TestStep"])
        
        registry.register(processor)
        
        assert len(registry.processors) == 1
        assert processor.initialized
        assert "TestProcessor" in registry.get_registered_processors()
        assert registry._processor_map["TestStep"] == processor
    
    def test_register_multiple_processors_priority_order(self):
        registry = StepProcessorRegistry()
        
        low_priority = MockProcessor("LowPriority", priority=100)
        high_priority = MockProcessor("HighPriority", priority=10)
        medium_priority = MockProcessor("MediumPriority", priority=50)
        
        # Register in random order
        registry.register(low_priority)
        registry.register(high_priority)
        registry.register(medium_priority)
        
        # Should be sorted by priority (lower number = higher priority)
        assert registry.processors[0].name == "HighPriority"
        assert registry.processors[1].name == "MediumPriority"
        assert registry.processors[2].name == "LowPriority"
    
    def test_unregister_processor(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", supported_types=["TestStep"])
        
        registry.register(processor)
        assert len(registry.processors) == 1
        
        success = registry.unregister("TestProcessor")
        assert success
        assert len(registry.processors) == 0
        assert processor.finalized
        assert "TestStep" not in registry._processor_map
    
    def test_unregister_nonexistent_processor(self):
        registry = StepProcessorRegistry()
        success = registry.unregister("NonExistentProcessor")
        assert not success
    
    def test_find_processor_fast_lookup(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", supported_types=["ExtractStep"])
        registry.register(processor)
        
        # Create a mock step
        step = MagicMock()
        step.__class__.__name__ = "ExtractStep"
        
        found_processor = registry.find_processor(step)
        assert found_processor == processor
    
    def test_find_processor_fallback_search(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", supported_types=["OtherStep"])
        processor.can_handle = MagicMock(return_value=True)
        registry.register(processor)
        
        # Create a step not in fast lookup
        step = MagicMock()
        step.__class__.__name__ = "UnknownStep"
        
        found_processor = registry.find_processor(step)
        assert found_processor == processor
        processor.can_handle.assert_called_once_with(step)
    
    def test_find_processor_none_found(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", supported_types=["OtherStep"])
        processor.can_handle = MagicMock(return_value=False)
        registry.register(processor)
        
        step = MagicMock()
        step.__class__.__name__ = "UnknownStep"
        
        found_processor = registry.find_processor(step)
        assert found_processor is None
    
    def test_process_step_success(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", supported_types=["TestStep"])
        registry.register(processor)
        
        step = MagicMock()
        step.__class__.__name__ = "TestStep"
        context = MagicMock()
        page = MagicMock()
        
        results = registry.process_step(context, page, step)
        assert results == [{"mock_result": True}]
    
    def test_process_step_no_processor(self):
        registry = StepProcessorRegistry()
        
        step = MagicMock()
        step.__class__.__name__ = "UnknownStep"
        
        results = registry.process_step(MagicMock(), MagicMock(), step)
        assert results == []
    
    def test_process_step_processor_error(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", supported_types=["TestStep"])
        processor.execute = MagicMock(side_effect=Exception("Test error"))
        registry.register(processor)
        
        step = MagicMock()
        step.__class__.__name__ = "TestStep"
        
        results = registry.process_step(MagicMock(), MagicMock(), step)
        assert results == []  # Should return empty list on error
    
    def test_get_processor_info(self):
        registry = StepProcessorRegistry()
        processor = MockProcessor("TestProcessor", priority=42, supported_types=["TestStep", "OtherStep"])
        registry.register(processor)
        
        info = registry.get_processor_info("TestProcessor")
        assert info == {
            "name": "TestProcessor",
            "priority": 42,
            "supported_types": ["TestStep", "OtherStep"],
            "class": "MockProcessor"
        }
    
    def test_get_processor_info_not_found(self):
        registry = StepProcessorRegistry()
        info = registry.get_processor_info("NonExistent")
        assert info is None


class TestStepProcessor:
    
    def test_processor_defaults(self):
        processor = MockProcessor()
        assert processor.name == "MockProcessor"
        assert processor.priority == 100
        assert hasattr(processor, 'logger')
    
    def test_lifecycle_methods(self):
        processor = MockProcessor()
        
        # Initial state
        assert not processor.initialized
        assert not processor.finalized
        
        # Initialize
        processor.initialize()
        assert processor.initialized
        
        # Finalize
        processor.finalize()
        assert processor.finalized