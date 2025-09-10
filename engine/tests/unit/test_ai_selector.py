"""Tests for AI Selector processor."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from engine.web_engine.plugins.ai_selector import AISelectorProcessor, AIConfig
from engine.web_engine.models import AiSelectStep


class TestAISelectorProcessor:
    """Test cases for AI Selector processor."""
    
    @pytest.fixture
    def config(self):
        """Create test AI config."""
        return AIConfig(
            endpoint="https://test-api.com/chat/completions",
            api_key="test-key",
            model="test-model",
            temperature=0.3,
            max_tokens=500,
            timeout=30
        )
    
    @pytest.fixture
    def processor(self, config):
        """Create AI selector processor instance."""
        return AISelectorProcessor(config)
    
    @pytest.fixture
    def mock_page(self):
        """Create a mock page object."""
        page = Mock()
        page.url = "https://example.com"
        page.title.return_value = "Test Page"
        page.content.return_value = "<html><body><h1>Test</h1></body></html>"
        
        # Mock query_selector_all for structure extraction
        def mock_query_selector_all(selector):
            if selector == "h1":
                el = Mock()
                el.text_content.return_value = "Test Heading"
                el.get_attribute.return_value = "heading-class"
                el.tag_name = "h1"
                return [el]
            elif "[class*='price']" in selector:
                el = Mock()
                el.text_content.return_value = "$19.99"
                el.get_attribute.return_value = "price-value"
                el.tag_name = "span"
                return [el]
            return []
        
        page.query_selector_all = mock_query_selector_all
        return page
    
    def test_can_handle_ai_step(self, processor):
        """Test that processor can handle AI selection steps."""
        ai_step = AiSelectStep(**{"@ai-select": "test description"})
        assert processor.can_handle(ai_step)
    
    def test_cannot_handle_non_ai_step(self, processor):
        """Test that processor cannot handle non-AI steps."""
        non_ai_step = Mock()
        assert not processor.can_handle(non_ai_step)
    
    def test_supported_step_types(self, processor):
        """Test that processor returns correct supported types."""
        supported = processor.get_supported_step_types()
        assert supported == ["AiSelectStep"]
    
    def test_extract_page_structure(self, processor, mock_page):
        """Test page structure extraction."""
        structure = processor._extract_page_structure(mock_page)
        
        assert "URL: https://example.com" in structure
        assert "Title: Test Page" in structure
        assert "Sample HTML structure:" in structure
        assert "Test Heading" in structure
    
    def test_generate_cache_key(self, processor):
        """Test cache key generation."""
        key1 = processor._generate_cache_key("url1", "desc1", "structure1")
        key2 = processor._generate_cache_key("url1", "desc1", "structure1")
        key3 = processor._generate_cache_key("url2", "desc1", "structure1")
        
        assert key1 == key2  # Same inputs = same key
        assert key1 != key3  # Different inputs = different key
        assert len(key1) == 32  # MD5 hash length
    
    def test_fallback_selector_price(self, processor):
        """Test fallback selector for price."""
        xpath = processor._fallback_selector("product price")
        assert "price" in xpath.lower()
        assert "//" in xpath
    
    def test_fallback_selector_title(self, processor):
        """Test fallback selector for title."""
        xpath = processor._fallback_selector("product title")
        assert "h1" in xpath or "title" in xpath.lower()
    
    def test_fallback_selector_generic(self, processor):
        """Test fallback selector for unknown terms."""
        xpath = processor._fallback_selector("some unknown element")
        assert xpath == "//*[text() and not(self::script) and not(self::style)]"
    
    @patch('requests.post')
    def test_get_ai_selector_success(self, mock_post, processor):
        """Test successful AI selector generation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "//span[@class='price']"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        xpath = processor._get_ai_selector("product price", "test structure")
        
        assert xpath == "//span[@class='price']"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_get_ai_selector_api_error(self, mock_post, processor):
        """Test AI selector generation with API error."""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        xpath = processor._get_ai_selector("product price", "test structure")
        
        # Should fallback to pattern-based selector
        assert xpath is not None
        assert "price" in xpath.lower()  # Should use price fallback
        assert "price" in xpath.lower()
    
    def test_get_ai_selector_no_api_key(self, processor):
        """Test AI selector without API key."""
        processor.config.api_key = None
        
        xpath = processor._get_ai_selector("product price", "test structure")
        
        # Should use fallback
        assert xpath is not None
        assert "price" in xpath.lower()
    
    def test_execute_xpath(self, processor, mock_page):
        """Test XPath execution and result extraction."""
        # Mock elements found by XPath
        mock_element1 = Mock()
        mock_element1.text_content.return_value = " $19.99 "  # With whitespace
        mock_element1.get_attribute.side_effect = lambda attr: {
            "href": None,
            "src": None,
            "alt": None,
            "title": "Price"
        }.get(attr)
        
        mock_element2 = Mock()
        mock_element2.text_content.return_value = " $29.99 "
        mock_element2.get_attribute.side_effect = lambda attr: None
        
        # Mock query_selector_all to return elements when called with xpath= prefix
        def mock_query_selector_all(selector):
            if selector == "xpath=//span[@class='price']":
                return [mock_element1, mock_element2]
            return []
        
        mock_page.query_selector_all = mock_query_selector_all
        
        results = processor._execute_xpath(mock_page, "//span[@class='price']", 10)
        
        assert len(results) == 2
        assert results[0]["text"] == "$19.99"
        assert results[0]["title"] == "Price"
        assert results[0]["xpath_used"] == "//span[@class='price']"
        assert results[1]["text"] == "$29.99"
    
    def test_execute_xpath_with_url(self, processor, mock_page):
        """Test XPath execution with URL extraction."""
        mock_element = Mock()
        mock_element.text_content.return_value = " Click here "
        mock_element.get_attribute.side_effect = lambda attr: {
            "href": "https://example.com/link",
            "src": None,
            "alt": None,
            "title": None
        }.get(attr)
        
        # Mock query_selector_all with xpath= prefix
        def mock_query_selector_all(selector):
            if selector == "xpath=//a":
                return [mock_element]
            return []
        
        mock_page.query_selector_all = mock_query_selector_all
        
        results = processor._execute_xpath(mock_page, "//a", 10)
        
        assert len(results) == 1
        assert results[0]["text"] == "Click here"
        assert results[0]["url"] == "https://example.com/link"
    
    def test_execute_xpath_no_elements(self, processor, mock_page):
        """Test XPath execution with no matching elements."""
        mock_page.query_selector_all.return_value = []
        
        results = processor._execute_xpath(mock_page, "//nonexistent", 10)
        
        assert results == []
    
    @patch('requests.post')
    def test_execute_with_cache(self, mock_post, processor, mock_page):
        """Test execution with caching."""
        step = AiSelectStep(**{"@ai-select": "test element"})
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "//div[@class='test']"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Mock element found
        mock_element = Mock()
        mock_element.text_content.return_value = "Test content"
        mock_element.get_attribute.return_value = None
        # Mock query_selector_all with xpath= prefix
        def mock_query_selector_all(selector):
            if selector.startswith("xpath="):
                return [mock_element]
            return []
        
        mock_page.query_selector_all = mock_query_selector_all
        
        # First execution - should call API
        results1 = processor.execute(None, mock_page, step)
        assert len(results1) == 1
        assert mock_post.call_count == 1
        
        # Second execution - should use cache
        results2 = processor.execute(None, mock_page, step)
        assert len(results2) == 1
        assert mock_post.call_count == 1  # No additional API call
    
    def test_execute_max_results_limit(self, processor, mock_page):
        """Test max results limiting."""
        step = AiSelectStep(**{"@ai-select": "test element", "@max-results": 2})
        
        # Mock multiple elements
        elements = []
        for i in range(5):
            el = Mock()
            el.text_content.return_value = f"Element {i}"
            el.get_attribute.return_value = None
            elements.append(el)
        
        # Mock query_selector_all with xpath= prefix
        def mock_query_selector_all(selector):
            if selector.startswith("xpath="):
                return elements
            return []
        
        mock_page.query_selector_all = mock_query_selector_all
        processor.cache["test_key"] = "//div"
        
        # Mock cache key generation to use known key
        processor._generate_cache_key = Mock(return_value="test_key")
        
        results = processor.execute(None, mock_page, step)
        
        assert len(results) == 2  # Should limit to max_results
        assert results[0]["text"] == "Element 0"
        assert results[1]["text"] == "Element 1"
    
    def test_execute_with_exception(self, processor, mock_page):
        """Test execution with exception handling."""
        step = AiSelectStep(**{"@ai-select": "test element"})
        
        # Mock exception during execution
        mock_page.query_selector_all.side_effect = Exception("Test error")
        
        results = processor.execute(None, mock_page, step)
        
        assert results == []  # Should return empty list on error