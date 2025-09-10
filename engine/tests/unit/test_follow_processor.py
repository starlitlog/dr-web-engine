"""
Tests for the enhanced FollowStepProcessor with recursive navigation.
"""

import pytest
from unittest.mock import MagicMock, patch

from engine.web_engine.follow_processor import FollowStepProcessor
from engine.web_engine.models import FollowStep, ExtractStep


class TestFollowStepProcessor:
    
    def test_can_handle_follow_step(self):
        processor = FollowStepProcessor()
        follow_step = FollowStep(**{
            "@xpath": ".//a/@href",
            "@steps": [{"@xpath": "//h1", "@fields": {"title": "text()"}}]
        })
        
        assert processor.can_handle(follow_step) is True
    
    def test_cannot_handle_extract_step(self):
        processor = FollowStepProcessor()
        extract_step = ExtractStep(**{
            "@xpath": "//div",
            "@fields": {"title": "text()"}
        })
        
        assert processor.can_handle(extract_step) is False
    
    def test_get_supported_step_types(self):
        processor = FollowStepProcessor()
        assert processor.get_supported_step_types() == ["FollowStep"]
    
    def test_priority_setting(self):
        processor = FollowStepProcessor()
        assert processor.priority == 30  # Higher precedence than Extract (50) and Conditional (40)
    
    def test_is_external_link(self):
        processor = FollowStepProcessor()
        
        # Same domain
        assert processor._is_external_link(
            "https://example.com/page2", 
            "https://example.com/page1"
        ) is False
        
        # Different domain  
        assert processor._is_external_link(
            "https://other.com/page", 
            "https://example.com/page1"
        ) is True
        
        # Relative link (no domain)
        assert processor._is_external_link(
            "/page2",
            "https://example.com/page1" 
        ) is False
    
    def test_is_valid_url(self):
        processor = FollowStepProcessor()
        
        # Valid URLs
        assert processor._is_valid_url("https://example.com/page") is True
        assert processor._is_valid_url("http://example.com/page") is True
        
        # Invalid URLs
        assert processor._is_valid_url("ftp://example.com/page") is False
        assert processor._is_valid_url("not-a-url") is False
        assert processor._is_valid_url("") is False
    
    @patch('engine.web_engine.follow_processor.FollowStepProcessor._execute_steps_on_page')
    def test_navigate_recursive_depth_limit(self, mock_execute_steps):
        processor = FollowStepProcessor()
        
        # Mock page and context
        page = MagicMock()
        page.url = "https://example.com"
        
        # Mock the element that represents a link
        mock_element = MagicMock()
        page.query_selector_all.return_value = [mock_element]
        
        # Mock the extractor to return a valid link
        processor.extractor.extract_value = MagicMock(return_value="https://example.com/page2")
        
        context = MagicMock()
        new_page = MagicMock()
        new_page.url = "https://example.com/page2"
        
        # Mock the new_page to have no more links (to prevent further recursion)
        new_page.query_selector_all.return_value = []
        
        # Set up context manager properly
        context.new_page.return_value.__enter__.return_value = new_page
        context.new_page.return_value.__exit__.return_value = None
        
        follow_step = FollowStep(**{
            "@xpath": ".//a/@href",
            "@steps": [{"@xpath": "//h1", "@fields": {"title": "text()"}}],
            "@max-depth": 1
        })
        
        mock_execute_steps.return_value = [{"title": "Test"}]
        
        results = []
        visited_urls = set()
        
        # This should only go 1 level deep
        processor._navigate_recursive(
            context, page, follow_step, results, visited_urls, 
            current_depth=0, base_url="https://example.com"
        )
        
        # Should have executed steps once (at depth 1)
        assert mock_execute_steps.call_count == 1
    
    @patch('engine.web_engine.follow_processor.FollowStepProcessor._execute_steps_on_page')
    def test_navigate_recursive_cycle_detection(self, mock_execute_steps):
        processor = FollowStepProcessor()
        
        # Mock page that always returns the same link (would cause cycle)
        page = MagicMock()
        page.url = "https://example.com/page1"
        page.query_selector_all.return_value = [
            MagicMock(get_attribute=lambda x: "https://example.com/page1")  # Same URL = cycle
        ]
        
        context = MagicMock()
        
        follow_step = FollowStep(**{
            "@xpath": ".//a/@href", 
            "@steps": [{"@xpath": "//h1", "@fields": {"title": "text()"}}],
            "@detect-cycles": True
        })
        
        results = []
        visited_urls = set()
        
        processor._navigate_recursive(
            context, page, follow_step, results, visited_urls,
            current_depth=0, base_url="https://example.com/page1"
        )
        
        # Should not execute steps because cycle was detected
        assert mock_execute_steps.call_count == 0
    
    def test_extract_links(self):
        processor = FollowStepProcessor()
        
        # Mock page with links
        mock_element1 = MagicMock()
        mock_element2 = MagicMock()
        
        page = MagicMock()
        page.query_selector_all.return_value = [mock_element1, mock_element2]
        
        # Mock extractor
        processor.extractor.extract_value = MagicMock(side_effect=[
            "https://example.com/page1",
            "https://example.com/page2"
        ])
        
        links = processor._extract_links(page, ".//a/@href", "https://example.com")
        
        assert len(links) == 2
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        
        # Check XPath query was made
        page.query_selector_all.assert_called_once_with("xpath=.//a/@href")
    
    def test_extract_links_filters_invalid_urls(self):
        processor = FollowStepProcessor()
        
        mock_element = MagicMock()
        page = MagicMock()
        page.query_selector_all.return_value = [mock_element]
        
        # Mock extractor returning invalid URL
        processor.extractor.extract_value = MagicMock(return_value="not-a-url")
        
        links = processor._extract_links(page, ".//a/@href", "https://example.com")
        
        assert len(links) == 0  # Invalid URL should be filtered out