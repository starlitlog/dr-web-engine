"""Tests for API Extractor processor."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from engine.web_engine.plugins.api_extractor import ApiExtractorProcessor
from engine.web_engine.models import ApiStep


class TestApiExtractorProcessor:
    """Test cases for API Extractor processor."""
    
    @pytest.fixture
    def processor(self):
        """Create an API extractor processor instance."""
        return ApiExtractorProcessor()
    
    @pytest.fixture
    def mock_page(self):
        """Create a mock page object."""
        page = Mock()
        page.on = Mock()
        page.wait_for_load_state = Mock()
        return page
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock response object."""
        response = Mock()
        response.url = "https://api.example.com/products/123"
        response.status = 200
        response.headers = {"content-type": "application/json"}
        response.request.method = "GET"
        response.request.timing = {"startTime": 1000}
        return response
    
    def test_can_handle_api_step(self, processor):
        """Test that processor can handle API steps."""
        api_step = ApiStep()
        assert processor.can_handle(api_step)
    
    def test_cannot_handle_non_api_step(self, processor):
        """Test that processor cannot handle non-API steps."""
        non_api_step = Mock()
        assert not processor.can_handle(non_api_step)
    
    def test_supported_step_types(self, processor):
        """Test that processor returns correct supported types."""
        supported = processor.get_supported_step_types()
        assert supported == ["ApiStep"]
    
    def test_matches_endpoint_pattern_with_regex(self, processor):
        """Test endpoint pattern matching with regex."""
        # Test regex pattern matching
        assert processor._matches_endpoint_pattern(
            "https://api.example.com/products/123",
            r"/products/\d+"
        )
        
        assert not processor._matches_endpoint_pattern(
            "https://api.example.com/users/abc",
            r"/products/\d+"
        )
    
    def test_matches_endpoint_pattern_without_pattern(self, processor):
        """Test endpoint pattern matching without specific pattern."""
        # Should match common API patterns
        assert processor._matches_endpoint_pattern(
            "https://api.example.com/api/products", None
        )
        
        assert processor._matches_endpoint_pattern(
            "https://example.com/rest/users", None
        )
        
        assert processor._matches_endpoint_pattern(
            "https://example.com/v1/data", None
        )
        
        assert processor._matches_endpoint_pattern(
            "https://example.com/data.json", None
        )
        
        # Should not match non-API URLs
        assert not processor._matches_endpoint_pattern(
            "https://example.com/about", None
        )
    
    def test_matches_endpoint_pattern_with_string(self, processor):
        """Test endpoint pattern matching with simple string."""
        assert processor._matches_endpoint_pattern(
            "https://api.example.com/products/123",
            "products"
        )
        
        assert not processor._matches_endpoint_pattern(
            "https://api.example.com/users/123",
            "products"
        )
    
    def test_extract_data_from_json_response(self, processor):
        """Test extracting data from JSON response."""
        step = ApiStep(response_type="json")
        
        # Test with dict response
        data = {"id": 123, "name": "Product", "price": 99.99}
        result = processor._extract_data_from_response(data, step)
        assert result == data
        
        # Test with JSON string
        json_string = json.dumps(data)
        result = processor._extract_data_from_response(json_string, step)
        assert result == data
    
    def test_extract_data_with_fields_filter(self, processor):
        """Test extracting specific fields from response."""
        step = ApiStep()
        step.response_type = "json"
        step.fields = ["id", "name"]
        
        data = {"id": 123, "name": "Product", "price": 99.99, "description": "..."}
        result = processor._extract_data_from_response(data, step)
        
        expected = {"id": 123, "name": "Product"}
        assert result == expected
    
    def test_extract_data_with_fields_filter_from_list(self, processor):
        """Test extracting fields from list response."""
        step = ApiStep()
        step.response_type = "json"
        step.fields = ["id", "name"]
        
        data = [
            {"id": 1, "name": "Product 1", "price": 10},
            {"id": 2, "name": "Product 2", "price": 20}
        ]
        result = processor._extract_data_from_response(data, step)
        
        expected = [
            {"id": 1, "name": "Product 1"},
            {"id": 2, "name": "Product 2"}
        ]
        assert result == expected
    
    def test_extract_data_with_json_path(self, processor):
        """Test extracting data using JSONPath."""
        step = ApiStep()
        step.response_type = "json"
        step.json_path = "$.data.products"
        
        data = {
            "status": "success",
            "data": {
                "products": [
                    {"id": 1, "name": "Product 1"},
                    {"id": 2, "name": "Product 2"}
                ]
            }
        }
        
        result = processor._extract_data_from_response(data, step)
        expected = [
            {"id": 1, "name": "Product 1"},
            {"id": 2, "name": "Product 2"}
        ]
        assert result == expected
    
    def test_apply_json_path_simple(self, processor):
        """Test simple JSONPath application."""
        data = {"user": {"name": "John", "age": 30}}
        
        result = processor._apply_json_path(data, "user.name")
        assert result == "John"
        
        result = processor._apply_json_path(data, "$.user.age")
        assert result == 30
    
    def test_apply_json_path_with_array_index(self, processor):
        """Test JSONPath with array index."""
        data = {"users": [{"name": "John"}, {"name": "Jane"}]}
        
        result = processor._apply_json_path(data, "users[0].name")
        assert result == "John"
        
        result = processor._apply_json_path(data, "users[1].name")
        assert result == "Jane"
    
    def test_apply_json_path_invalid_path(self, processor):
        """Test JSONPath with invalid path."""
        data = {"user": {"name": "John"}}
        
        # Non-existent field should return None
        result = processor._apply_json_path(data, "user.email")
        assert result is None
        
        # Invalid array index should return None
        result = processor._apply_json_path(data, "user[0]")
        assert result is None
    
    def test_extract_data_from_text_response(self, processor):
        """Test extracting data from text response."""
        step = ApiStep(response_type="text")
        
        text_data = "Product: Laptop, Price: $999"
        result = processor._extract_data_from_response(text_data, step)
        
        expected = {"text": text_data}
        assert result == expected
    
    def test_extract_data_from_empty_response(self, processor):
        """Test extracting data from empty response."""
        step = ApiStep(response_type="json")
        
        # Empty string should return None
        result = processor._extract_data_from_response("", step)
        assert result is None
        
        # None should return None
        result = processor._extract_data_from_response(None, step)
        assert result is None
    
    def test_process_intercepted_requests(self, processor):
        """Test processing intercepted requests."""
        step = ApiStep()
        step.name = "test_api"
        step.fields = ["id", "name"]
        
        # Mock intercepted request data
        processor.intercepted_requests = [
            {
                "url": "https://api.example.com/products/123",
                "method": "GET",
                "status": 200,
                "body": {"id": 123, "name": "Product", "price": 99.99}
            }
        ]
        
        results = processor._process_intercepted_requests(step)
        
        assert len(results) == 1
        result = results[0]
        assert result["url"] == "https://api.example.com/products/123"
        assert result["method"] == "GET"
        assert result["status"] == 200
        assert result["source"] == "test_api"
        assert result["data"] == {"id": 123, "name": "Product"}
    
    @patch('time.sleep')
    def test_wait_for_api_calls(self, mock_sleep, processor, mock_page):
        """Test waiting for API calls."""
        step = ApiStep()
        step.timeout = 5000  # Directly set the attribute
        
        processor._wait_for_api_calls(mock_page, step)
        
        mock_page.wait_for_load_state.assert_called_once_with(
            "networkidle", timeout=5000
        )
        mock_sleep.assert_called_once_with(1)
    
    @patch('time.sleep')
    def test_wait_for_api_calls_with_timeout(self, mock_sleep, processor, mock_page):
        """Test waiting for API calls with timeout exception."""
        step = ApiStep()
        step.timeout = 5000
        mock_page.wait_for_load_state.side_effect = Exception("Timeout")
        
        # Should not raise exception, just continue
        processor._wait_for_api_calls(mock_page, step)
        
        mock_page.wait_for_load_state.assert_called_once()
        mock_sleep.assert_called_once_with(1)
    
    def test_execute_method_basic(self, processor, mock_page):
        """Test basic execute method flow."""
        step = ApiStep(endpoint_pattern="products")
        context = Mock()
        
        with patch.object(processor, '_setup_network_monitoring') as mock_setup, \
             patch.object(processor, '_wait_for_api_calls') as mock_wait, \
             patch.object(processor, '_process_intercepted_requests') as mock_process:
            
            mock_process.return_value = [{"test": "data"}]
            
            result = processor.execute(context, mock_page, step)
            
            mock_setup.assert_called_once_with(mock_page, step)
            mock_wait.assert_called_once_with(mock_page, step)
            mock_process.assert_called_once_with(step)
            assert result == [{"test": "data"}]
    
    def test_execute_method_with_exception(self, processor, mock_page):
        """Test execute method with exception."""
        step = ApiStep()
        context = Mock()
        
        with patch.object(processor, '_setup_network_monitoring', side_effect=Exception("Test error")):
            result = processor.execute(context, mock_page, step)
            assert result == []
    
    def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor.priority == 30
        assert processor.intercepted_requests == []
        assert hasattr(processor, 'logger')