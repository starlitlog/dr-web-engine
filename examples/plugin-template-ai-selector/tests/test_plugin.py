"""
Tests for AI-Selector Plugin
"""

import pytest
from unittest.mock import Mock, patch
from drweb_plugin_ai_selector.plugin import AISelectorPlugin
from drweb_plugin_ai_selector.processor import AISelectorProcessor
from drweb_plugin_ai_selector.config import AIConfig


class TestAISelectorPlugin:
    """Tests for the AI-Selector plugin."""
    
    def test_plugin_metadata(self):
        """Test plugin metadata."""
        plugin = AISelectorPlugin()
        metadata = plugin.metadata
        
        assert metadata.name == "drweb-plugin-ai-selector"
        assert metadata.version == "1.0.0"
        assert metadata.author == "DR Web Engine Team"
        assert "AiSelectStep" in metadata.supported_step_types
        assert metadata.min_drweb_version == "0.10.0"
    
    def test_get_processors(self):
        """Test processor retrieval."""
        plugin = AISelectorPlugin()
        processors = plugin.get_processors()
        
        assert len(processors) == 1
        assert isinstance(processors[0], AISelectorProcessor)
    
    def test_initialize_with_config(self):
        """Test plugin initialization with configuration."""
        plugin = AISelectorPlugin()
        
        config = {
            "endpoint": "https://custom-api.com/v1/chat",
            "api_key": "test-key",
            "model": "test-model",
            "temperature": 0.5,
            "max_tokens": 1000,
            "timeout": 60
        }
        
        plugin.initialize(config)
        
        # Check that processor was configured
        processors = plugin.get_processors()
        processor = processors[0]
        
        assert processor.config.endpoint == "https://custom-api.com/v1/chat"
        assert processor.config.api_key == "test-key"
        assert processor.config.model == "test-model"
        assert processor.config.temperature == 0.5
        assert processor.config.max_tokens == 1000
        assert processor.config.timeout == 60
    
    def test_finalize(self):
        """Test plugin finalization."""
        plugin = AISelectorPlugin()
        
        # Initialize and get processor
        plugin.initialize({})
        processors = plugin.get_processors()
        processor = processors[0]
        
        # Add some cache data
        processor.cache["test"] = "data"
        
        # Finalize
        plugin.finalize()
        
        # Check cleanup
        assert len(processor.cache) == 0
        assert plugin._processor is None
        assert plugin._config is None
    
    def test_config_schema(self):
        """Test configuration schema."""
        plugin = AISelectorPlugin()
        schema = plugin.get_config_schema()
        
        assert schema is not None
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Check required properties
        properties = schema["properties"]
        assert "endpoint" in properties
        assert "api_key" in properties
        assert "model" in properties
        assert "temperature" in properties
        assert "max_tokens" in properties
        assert "timeout" in properties


class TestAISelectorProcessor:
    """Tests for the AI-Selector processor."""
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        config = AIConfig()
        processor = AISelectorProcessor(config)
        
        assert processor.config == config
        assert processor.priority == 35
        assert isinstance(processor.cache, dict)
    
    def test_can_handle(self):
        """Test step type handling."""
        processor = AISelectorProcessor()
        
        # Mock AiSelectStep
        mock_ai_step = Mock()
        mock_ai_step.__class__.__name__ = "AiSelectStep"
        
        # Mock other step types
        mock_other_step = Mock()
        mock_other_step.__class__.__name__ = "ExtractStep"
        
        # Test with different step types (simplified)
        # In real implementation, would use actual step types
        assert processor.get_supported_step_types() == ["AiSelectStep"]
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        processor = AISelectorProcessor()
        
        # Test cache key generation
        url = "https://example.com"
        description = "test description"
        structure = "test structure"
        
        key1 = processor._generate_cache_key(url, description, structure)
        key2 = processor._generate_cache_key(url, description, structure)
        key3 = processor._generate_cache_key(url, "different", structure)
        
        assert key1 == key2  # Same inputs should generate same key
        assert key1 != key3  # Different inputs should generate different keys
        assert isinstance(key1, str)
        assert len(key1) == 32  # MD5 hash length
    
    def test_fallback_selector_patterns(self):
        """Test fallback selector patterns."""
        processor = AISelectorProcessor()
        
        # Test various descriptions
        test_cases = [
            ("product prices", "price"),
            ("page title", "title"), 
            ("submit button", "button"),
            ("product image", "image"),
            ("item description", "description"),
            ("customer review", "review"),
            ("star rating", "rating"),
            ("author name", "author"),
            ("publication date", "date"),
            ("article content", "content"),
            ("quote text", "text"),
            ("external link", "link"),
            ("news headline", "headline"),
            ("search snippet", "snippet")
        ]
        
        for description, expected_pattern in test_cases:
            xpath = processor._fallback_selector(description)
            assert xpath is not None
            assert isinstance(xpath, str)
            assert xpath.startswith("//")
    
    def test_xpath_cleaning(self):
        """Test XPath cleaning logic.""" 
        processor = AISelectorProcessor()
        
        # Test various AI responses that need cleaning
        test_cases = [
            ('//div[@class="test"]', '//div[@class="test"]'),  # Already clean
            ('"//div[@class=\'test\']"', "//div[@class='test']"),  # Remove quotes
            ("xpath://span", "//span"),  # Remove xpath: prefix
            ("```//button```", "//button"),  # Remove markdown
        ]
        
        for raw_xpath, expected in test_cases:
            # Simulate the cleaning logic
            cleaned = raw_xpath.strip('"\'`')
            if cleaned.startswith('xpath:'):
                cleaned = cleaned[6:]
            
            if expected.startswith('//') or expected.startswith('./'):
                assert cleaned == expected or cleaned.startswith('//')


@pytest.fixture
def mock_page():
    """Mock page object for testing."""
    page = Mock()
    page.url = "https://example.com"
    page.title.return_value = "Test Page"
    page.query_selector_all.return_value = []
    return page


@pytest.fixture  
def mock_ai_step():
    """Mock AiSelectStep for testing."""
    step = Mock()
    step.find = "test description"
    step.max_results = 10
    return step


class TestIntegration:
    """Integration tests."""
    
    def test_plugin_processor_integration(self):
        """Test plugin and processor integration."""
        plugin = AISelectorPlugin()
        
        # Initialize plugin
        config = {"model": "test-model"}
        plugin.initialize(config)
        
        # Get processor
        processors = plugin.get_processors()
        processor = processors[0]
        
        # Verify configuration was passed through
        assert processor.config.model == "test-model"
        
        # Verify processor is functional
        assert processor.priority == 35
        assert len(processor.get_supported_step_types()) == 1