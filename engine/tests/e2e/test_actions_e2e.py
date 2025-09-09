import pytest
import json
from pathlib import Path
from engine.web_engine.engine import execute_query
from engine.web_engine.models import ExtractionQuery
from engine.web_engine.base.playwright_browser import PlaywrightClient


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Playwright browser installation and network access")
def test_actions_with_javascript_site():
    """Test actions work with JavaScript-heavy site that requires interaction"""
    query_data = {
        "@url": "https://quotes.toscrape.com/js/",
        "@actions": [
            {
                "@type": "wait",
                "@until": "element", 
                "@selector": ".quote",
                "@timeout": 10000
            },
            {
                "@type": "scroll",
                "@direction": "down",
                "@pixels": 500
            },
            {
                "@type": "wait",
                "@until": "timeout",
                "@timeout": 2000
            }
        ],
        "@steps": [
            {
                "@xpath": "//div[@class='quote']",
                "@name": "quotes",
                "@fields": {
                    "text": ".//span[@class='text']/text()",
                    "author": ".//small[@class='author']/text()",
                    "tags": ".//div[@class='tags']//a/text()"
                }
            }
        ]
    }
    
    query = ExtractionQuery(**query_data)
    browser_client = PlaywrightClient()
    
    try:
        results = execute_query(query, browser_client)
        
        # Verify we got results
        assert len(results) > 0
        
        # Verify structure of first result
        first_quote = results[0]
        assert "text" in first_quote
        assert "author" in first_quote
        assert "tags" in first_quote
        
        # Verify content looks reasonable
        assert first_quote["text"] is not None
        assert first_quote["author"] is not None
        assert len(first_quote["text"]) > 10  # Should be a meaningful quote
        
    finally:
        browser_client.close()


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Playwright browser installation and network access")
def test_actions_with_infinite_scroll():
    """Test scroll actions with infinite scroll content"""
    query_data = {
        "@url": "https://infinite-scroll.com/demo/full-page/",
        "@actions": [
            {
                "@type": "wait",
                "@until": "element",
                "@selector": ".post",
                "@timeout": 5000
            },
            {
                "@type": "scroll",
                "@direction": "down",
                "@pixels": 800
            },
            {
                "@type": "wait",
                "@until": "timeout",
                "@timeout": 2000
            },
            {
                "@type": "scroll",
                "@direction": "down", 
                "@pixels": 800
            },
            {
                "@type": "wait",
                "@until": "network-idle",
                "@timeout": 10000
            }
        ],
        "@steps": [
            {
                "@xpath": "//article[contains(@class, 'post')]",
                "@name": "posts",
                "@fields": {
                    "title": ".//h2/text()",
                    "content": ".//p/text()"
                }
            }
        ]
    }
    
    query = ExtractionQuery(**query_data)
    browser_client = PlaywrightClient()
    
    try:
        results = execute_query(query, browser_client)
        
        # Should have loaded multiple posts due to scrolling
        assert len(results) >= 6  # Initial posts + scrolled posts
        
        # Verify structure
        for post in results[:3]:  # Check first 3 posts
            assert "title" in post
            assert "content" in post
            assert post["title"] is not None
            
    finally:
        browser_client.close()


@pytest.mark.e2e 
@pytest.mark.skip(reason="Requires test form site - enable when available")
def test_form_fill_actions():
    """Test form filling and submission actions"""
    query_data = {
        "@url": "https://httpbin.org/forms/post",
        "@actions": [
            {
                "@type": "fill",
                "@selector": "input[name='custname']",
                "@value": "Test User"
            },
            {
                "@type": "fill", 
                "@selector": "input[name='custtel']",
                "@value": "123-456-7890"
            },
            {
                "@type": "fill",
                "@selector": "input[name='custemail']",
                "@value": "test@example.com"
            },
            {
                "@type": "click",
                "@selector": "input[type='submit']"
            },
            {
                "@type": "wait",
                "@until": "element",
                "@selector": "pre",
                "@timeout": 5000
            }
        ],
        "@steps": [
            {
                "@xpath": "//pre",
                "@name": "response",
                "@fields": {
                    "content": ".//text()"
                }
            }
        ]
    }
    
    query = ExtractionQuery(**query_data)
    browser_client = PlaywrightClient()
    
    try:
        results = execute_query(query, browser_client)
        
        # Verify form was submitted and response received
        assert len(results) == 1
        response_content = results[0]["content"]
        
        # Should contain the submitted form data
        assert "Test User" in response_content
        assert "test@example.com" in response_content
        
    finally:
        browser_client.close()


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires hover-enabled test site - enable when available")
def test_hover_actions():
    """Test hover actions for dropdown menus"""
    query_data = {
        "@url": "https://example-site-with-dropdown.com",
        "@actions": [
            {
                "@type": "hover",
                "@selector": ".dropdown-trigger"
            },
            {
                "@type": "wait",
                "@until": "element",
                "@selector": ".dropdown-menu",
                "@timeout": 3000
            },
            {
                "@type": "click",
                "@selector": ".dropdown-menu .item"
            }
        ],
        "@steps": [
            {
                "@xpath": "//div[@class='content']",
                "@name": "content",
                "@fields": {
                    "text": ".//text()"
                }
            }
        ]
    }
    
    query = ExtractionQuery(**query_data)
    browser_client = PlaywrightClient()
    
    try:
        results = execute_query(query, browser_client)
        
        # Verify interaction worked
        assert len(results) > 0
        assert results[0]["text"] is not None
        
    finally:
        browser_client.close()


def test_example_actions_file_loads():
    """Test that example action files can be loaded and validated"""
    # Test the example_actions.json5 file
    query_data = {
        "@url": "https://quotes.toscrape.com/js/",
        "@actions": [
            {
                "@type": "wait",
                "@until": "element",
                "@selector": ".quote",
                "@timeout": 10000
            },
            {
                "@type": "scroll",
                "@direction": "down",
                "@pixels": 500
            },
            {
                "@type": "wait",
                "@until": "timeout",
                "@timeout": 2000
            }
        ],
        "@steps": [
            {
                "@xpath": "//div[@class='quote']",
                "@name": "quotes",
                "@fields": {
                    "text": ".//span[@class='text']/text()",
                    "author": ".//small[@class='author']/text()",
                    "tags": ".//div[@class='tags']//a/text()"
                }
            }
        ]
    }
    
    # Should validate without errors
    query = ExtractionQuery(**query_data)
    assert query.url == "https://quotes.toscrape.com/js/"
    assert len(query.actions) == 3
    assert len(query.steps) == 1
    
    # Verify action types
    assert query.actions[0].type == "wait"
    assert query.actions[1].type == "scroll"
    assert query.actions[2].type == "wait"


def test_complex_actions_file_loads():
    """Test that complex action files can be loaded and validated"""
    query_data = {
        "@url": "https://infinite-scroll.com/demo/full-page/",
        "@actions": [
            {
                "@type": "wait",
                "@until": "element",
                "@selector": ".post",
                "@timeout": 5000
            },
            {
                "@type": "scroll",
                "@direction": "down",
                "@pixels": 800
            },
            {
                "@type": "wait",
                "@until": "timeout",
                "@timeout": 2000
            },
            {
                "@type": "scroll",
                "@direction": "down", 
                "@pixels": 800
            },
            {
                "@type": "wait",
                "@until": "timeout",
                "@timeout": 2000
            },
            {
                "@type": "scroll",
                "@direction": "down",
                "@pixels": 800
            },
            {
                "@type": "wait",
                "@until": "network-idle",
                "@timeout": 10000
            }
        ],
        "@steps": [
            {
                "@xpath": "//article[contains(@class, 'post')]",
                "@name": "posts",
                "@fields": {
                    "title": ".//h2/text()",
                    "content": ".//p/text()"
                }
            }
        ]
    }
    
    # Should validate without errors
    query = ExtractionQuery(**query_data)
    assert query.url == "https://infinite-scroll.com/demo/full-page/"
    assert len(query.actions) == 7
    assert len(query.steps) == 1
    
    # Verify mix of action types
    action_types = [action.type for action in query.actions]
    assert "wait" in action_types
    assert "scroll" in action_types