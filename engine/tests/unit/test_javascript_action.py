"""
Tests for JavaScript actions.
"""

import pytest
from unittest.mock import MagicMock

from engine.web_engine.actions import JavaScriptActionHandler
from engine.web_engine.models import JavaScriptAction, ClickAction


class TestJavaScriptActionHandler:
    
    def test_can_handle_javascript_action(self):
        handler = JavaScriptActionHandler()
        js_action = JavaScriptAction(**{
            "@type": "javascript",
            "@code": "window.loadMore();"
        })
        
        assert handler.can_handle(js_action) is True
    
    def test_cannot_handle_click_action(self):
        handler = JavaScriptActionHandler()
        click_action = ClickAction(**{
            "@type": "click",
            "@selector": "#button"
        })
        
        assert handler.can_handle(click_action) is False
    
    def test_execute_simple_javascript(self):
        handler = JavaScriptActionHandler()
        page = MagicMock()
        page.evaluate.return_value = "success"
        
        js_action = JavaScriptAction(**{
            "@type": "javascript",
            "@code": "window.customFunction();"
        })
        
        result = handler.execute(page, js_action)
        
        assert result == "success"
        page.evaluate.assert_called_once_with("window.customFunction();")
    
    def test_execute_javascript_with_wait_condition(self):
        handler = JavaScriptActionHandler()
        page = MagicMock()
        page.evaluate.return_value = 5
        page.wait_for_function.return_value = True
        
        js_action = JavaScriptAction(**{
            "@type": "javascript",
            "@code": "return document.querySelectorAll('.item').length;",
            "@wait-for": "document.querySelectorAll('.item').length >= 5",
            "@timeout": 10000
        })
        
        result = handler.execute(page, js_action)
        
        assert result == 5
        page.evaluate.assert_called_once()
        page.wait_for_function.assert_called_once_with(
            "document.querySelectorAll('.item').length >= 5", 
            timeout=10000
        )
    
    def test_execute_javascript_wait_condition_fails(self):
        handler = JavaScriptActionHandler()
        page = MagicMock()
        page.evaluate.return_value = 2
        page.wait_for_function.side_effect = Exception("Timeout waiting for condition")
        
        js_action = JavaScriptAction(**{
            "@type": "javascript",
            "@code": "return document.querySelectorAll('.item').length;",
            "@wait-for": "document.querySelectorAll('.item').length >= 5"
        })
        
        result = handler.execute(page, js_action)
        
        # Should still return the result even if wait condition fails
        assert result == 2
        page.wait_for_function.assert_called_once()
    
    def test_execute_javascript_error(self):
        handler = JavaScriptActionHandler()
        page = MagicMock()
        page.evaluate.side_effect = Exception("JavaScript error")
        
        js_action = JavaScriptAction(**{
            "@type": "javascript",
            "@code": "throw new Error('test');"
        })
        
        result = handler.execute(page, js_action)
        
        assert result is None
    
    def test_execute_javascript_returns_none(self):
        handler = JavaScriptActionHandler()
        page = MagicMock()
        page.evaluate.return_value = None
        
        js_action = JavaScriptAction(**{
            "@type": "javascript",
            "@code": "console.log('no return');"
        })
        
        result = handler.execute(page, js_action)
        
        assert result is None