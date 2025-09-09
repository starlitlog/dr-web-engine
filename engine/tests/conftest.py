import pytest
from unittest.mock import MagicMock
from engine.web_engine.base.browser import BrowserClient


@pytest.fixture
def mock_browser_client():
    """Mock browser client for testing"""
    mock_client = MagicMock(spec=BrowserClient)
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    # Setup the context manager behavior
    mock_client.__enter__.return_value = mock_browser
    mock_client.__exit__.return_value = None
    
    # Setup browser chain
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    # Setup page methods
    mock_page.goto = MagicMock()
    mock_page.click = MagicMock()
    mock_page.fill = MagicMock()
    mock_page.hover = MagicMock()
    mock_page.evaluate = MagicMock()
    mock_page.wait_for_timeout = MagicMock()
    mock_page.wait_for_selector = MagicMock()
    mock_page.wait_for_load_state = MagicMock()
    mock_page.query_selector = MagicMock()
    mock_page.query_selector_all = MagicMock()
    
    return mock_client


@pytest.fixture
def mock_page():
    """Mock Playwright page for testing"""
    page = MagicMock()
    
    # Setup common page methods
    page.goto = MagicMock()
    page.click = MagicMock()
    page.fill = MagicMock()
    page.hover = MagicMock()
    page.evaluate = MagicMock()
    page.wait_for_timeout = MagicMock()
    page.wait_for_selector = MagicMock()
    page.wait_for_load_state = MagicMock()
    page.query_selector = MagicMock()
    page.query_selector_all = MagicMock()
    page.url = "https://example.com"
    
    return page


@pytest.fixture
def mock_element():
    """Mock Playwright element for testing"""
    element = MagicMock()
    
    # Setup element methods
    element.text_content = MagicMock(return_value="Test Text")
    element.get_attribute = MagicMock(return_value="test-value")
    element.query_selector = MagicMock()
    element.query_selector_all = MagicMock()
    element.scroll_into_view_if_needed = MagicMock()
    element.evaluate = MagicMock()
    
    return element


@pytest.fixture
def sample_extraction_query():
    """Sample extraction query for testing"""
    return {
        "@url": "https://example.com",
        "@steps": [
            {
                "@xpath": "//div[@class='item']",
                "@name": "items",
                "@fields": {
                    "title": ".//h2/text()",
                    "link": ".//a/@href"
                }
            }
        ]
    }


@pytest.fixture
def sample_query_with_actions():
    """Sample query with actions for testing"""
    return {
        "@url": "https://example.com",
        "@actions": [
            {"@type": "wait", "@until": "element", "@selector": ".content", "@timeout": 5000},
            {"@type": "click", "@selector": ".load-more"},
            {"@type": "scroll", "@direction": "down", "@pixels": 500}
        ],
        "@steps": [
            {
                "@xpath": "//div[@class='item']",
                "@name": "items", 
                "@fields": {
                    "title": ".//h2/text()",
                    "content": ".//p/text()"
                }
            }
        ]
    }


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests (require network/browser)")
    config.addinivalue_line("markers", "slow: Slow running tests")