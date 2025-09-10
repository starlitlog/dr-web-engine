"""
Tests for the JavaScriptStepProcessor.
"""

import pytest
from unittest.mock import MagicMock

from engine.web_engine.javascript_processor import JavaScriptStepProcessor, JavaScriptContext
from engine.web_engine.models import JavaScriptStep, ExtractStep


class TestJavaScriptStepProcessor:
    
    def test_can_handle_javascript_step(self):
        processor = JavaScriptStepProcessor()
        js_step = JavaScriptStep(**{
            "@javascript": "return document.title;"
        })
        
        assert processor.can_handle(js_step) is True
    
    def test_cannot_handle_extract_step(self):
        processor = JavaScriptStepProcessor()
        extract_step = ExtractStep(**{
            "@xpath": "//div",
            "@fields": {"title": "text()"}
        })
        
        assert processor.can_handle(extract_step) is False
    
    def test_get_supported_step_types(self):
        processor = JavaScriptStepProcessor()
        assert processor.get_supported_step_types() == ["JavaScriptStep"]
    
    def test_priority_setting(self):
        processor = JavaScriptStepProcessor()
        assert processor.priority == 20  # Higher precedence than most processors
    
    def test_execute_simple_javascript(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page
        page = MagicMock()
        page.evaluate.return_value = "Test Page Title"
        
        js_step = JavaScriptStep(**{
            "@javascript": "return document.title;",
            "@name": "page_title"
        })
        
        results = processor.execute(MagicMock(), page, js_step)
        
        assert len(results) == 1
        assert results[0] == {"page_title": "Test Page Title"}
        page.evaluate.assert_called_once_with("return document.title;", timeout=5000)
    
    def test_execute_javascript_returning_array(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page returning an array
        page = MagicMock()
        page.evaluate.return_value = [
            {"title": "Item 1", "price": "$10"},
            {"title": "Item 2", "price": "$20"}
        ]
        
        js_step = JavaScriptStep(**{
            "@javascript": "return extractData('.item', {title: 'h3', price: '.price'});",
            "@return-json": False
        })
        
        results = processor.execute(MagicMock(), page, js_step)
        
        assert len(results) == 2
        assert results[0] == {"title": "Item 1", "price": "$10"}
        assert results[1] == {"title": "Item 2", "price": "$20"}
    
    def test_execute_javascript_returning_object(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page returning a single object
        page = MagicMock()
        page.evaluate.return_value = {"total_items": 42, "page": 1}
        
        js_step = JavaScriptStep(**{
            "@javascript": "return {total_items: document.querySelectorAll('.item').length, page: 1};"
        })
        
        results = processor.execute(MagicMock(), page, js_step)
        
        assert len(results) == 1
        assert results[0] == {"total_items": 42, "page": 1}
    
    def test_execute_javascript_with_json_parsing(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page returning JSON string
        page = MagicMock()
        page.evaluate.return_value = '{"name": "John", "age": 30}'
        
        js_step = JavaScriptStep(**{
            "@javascript": "return JSON.stringify({name: 'John', age: 30});",
            "@return-json": True
        })
        
        results = processor.execute(MagicMock(), page, js_step)
        
        assert len(results) == 1
        assert results[0] == {"name": "John", "age": 30}
    
    def test_execute_javascript_json_parse_error(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page returning invalid JSON string
        page = MagicMock()
        page.evaluate.return_value = "invalid json {"
        
        js_step = JavaScriptStep(**{
            "@javascript": "return 'invalid json {';",
            "@return-json": True,
            "@name": "result"
        })
        
        results = processor.execute(MagicMock(), page, js_step)
        
        # Should fallback to raw string result
        assert len(results) == 1
        assert results[0] == {"result": "invalid json {"}
    
    def test_execute_javascript_returns_none(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page returning None
        page = MagicMock()
        page.evaluate.return_value = None
        
        js_step = JavaScriptStep(**{
            "@javascript": "console.log('no return value');"
        })
        
        results = processor.execute(MagicMock(), page, js_step)
        
        assert len(results) == 0
    
    def test_execute_javascript_with_timeout(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page
        page = MagicMock()
        page.evaluate.return_value = "result"
        
        js_step = JavaScriptStep(**{
            "@javascript": "return 'test';",
            "@timeout": 10000
        })
        
        processor.execute(MagicMock(), page, js_step)
        
        page.evaluate.assert_called_once_with("return 'test';", timeout=10000)
    
    def test_execute_javascript_error_handling(self):
        processor = JavaScriptStepProcessor()
        
        # Mock page that throws an error
        page = MagicMock()
        page.evaluate.side_effect = Exception("JavaScript execution failed")
        
        js_step = JavaScriptStep(**{
            "@javascript": "throw new Error('test error');"
        })
        
        results = processor.execute(MagicMock(), page, js_step)
        
        assert len(results) == 0


class TestJavaScriptContext:
    
    def test_get_common_utilities(self):
        utilities = JavaScriptContext.get_common_utilities()
        
        assert "extractText" in utilities
        assert "extractAttribute" in utilities
        assert "extractData" in utilities
        assert "waitForElements" in utilities
        assert "scrollAndWait" in utilities
    
    def test_wrap_code_with_utilities(self):
        user_code = "return extractText('.title');"
        wrapped = JavaScriptContext.wrap_code_with_utilities(user_code)
        
        assert "extractText" in wrapped
        assert "User code:" in wrapped
        assert user_code in wrapped