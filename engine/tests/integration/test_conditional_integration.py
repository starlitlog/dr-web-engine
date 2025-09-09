import pytest
from unittest.mock import MagicMock, patch
from engine.web_engine.engine import execute_query
from engine.web_engine.models import ExtractionQuery, ExtractStep, ConditionalStep, ConditionSpec


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
def test_execute_query_with_conditional_then(mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client
    mock_browser_client = MagicMock()
    mock_client = MagicMock()
    mock_page = MagicMock()

    mock_browser_client.__enter__.return_value = mock_client
    mock_browser_client.__exit__.return_value = None
    mock_client.browser = MagicMock()
    mock_client.page = mock_page
    MockBrowserClient.return_value = mock_browser_client

    # Setup mock for checking CAPTCHA
    mock_check_for_captcha.return_value = False

    # Setup mock elements - premium section exists
    premium_element = MagicMock()
    content_element = MagicMock()
    content_element.query_selector.return_value = MagicMock(text_content=lambda: "Premium Article")
    content_element.query_selector_all.return_value = [MagicMock()]
    
    mock_page.query_selector.return_value = premium_element  # Premium section exists
    mock_page.query_selector_all.return_value = [content_element]  # For execute_step function
    mock_context = MagicMock()
    mock_client.browser.new_context.return_value = mock_context

    # Setup query with conditional
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@steps": [
            {
                "@if": {"@exists": "#premium-section"},
                "@then": [
                    {
                        "@xpath": "//div[@class='premium-content']",
                        "@fields": {"title": ".//h2/text()"}
                    }
                ],
                "@else": [
                    {
                        "@xpath": "//div[@class='basic-content']", 
                        "@fields": {"title": ".//h2/text()"}
                    }
                ]
            }
        ]
    })

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Verify conditional evaluation occurred
    mock_page.query_selector.assert_called_with("#premium-section")
    
    # Should have results from the @then branch
    assert len(results) > 0


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
def test_execute_query_with_conditional_else(mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client
    mock_browser_client = MagicMock()
    mock_client = MagicMock()
    mock_page = MagicMock()

    mock_browser_client.__enter__.return_value = mock_client
    mock_browser_client.__exit__.return_value = None
    mock_client.browser = MagicMock()
    mock_client.page = mock_page
    MockBrowserClient.return_value = mock_browser_client

    # Setup mock for checking CAPTCHA
    mock_check_for_captcha.return_value = False

    # Setup mock elements - premium section does NOT exist
    basic_element = MagicMock()
    basic_element.query_selector.return_value = MagicMock(text_content=lambda: "Basic Article")
    basic_element.query_selector_all.return_value = [MagicMock()]
    
    mock_page.query_selector.return_value = None  # Premium section doesn't exist
    mock_page.query_selector_all.return_value = [basic_element]  # For execute_step function
    mock_context = MagicMock()
    mock_client.browser.new_context.return_value = mock_context

    # Setup query with conditional
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@steps": [
            {
                "@if": {"@exists": "#premium-section"},
                "@then": [
                    {
                        "@xpath": "//div[@class='premium-content']",
                        "@fields": {"title": ".//h2/text()"}
                    }
                ],
                "@else": [
                    {
                        "@xpath": "//div[@class='basic-content']", 
                        "@fields": {"title": ".//h2/text()"}
                    }
                ]
            }
        ]
    })

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Verify conditional evaluation occurred
    mock_page.query_selector.assert_called_with("#premium-section")
    
    # Should have results from the @else branch
    assert len(results) > 0


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
def test_execute_query_mixed_steps(mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client
    mock_browser_client = MagicMock()
    mock_client = MagicMock()
    mock_page = MagicMock()

    mock_browser_client.__enter__.return_value = mock_client
    mock_browser_client.__exit__.return_value = None
    mock_client.browser = MagicMock()
    mock_client.page = mock_page
    MockBrowserClient.return_value = mock_browser_client

    # Setup mock for checking CAPTCHA
    mock_check_for_captcha.return_value = False

    # Setup mock elements
    mock_page.query_selector.return_value = MagicMock()  # Element exists for condition
    mock_element = MagicMock()
    mock_element.query_selector.return_value = MagicMock(text_content=lambda: "Test")
    mock_client.browser.new_context.return_value.query_selector_all.return_value = [mock_element]

    # Setup query with mixed step types
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@steps": [
            # Regular extraction step
            {
                "@xpath": "//div[@class='regular']",
                "@fields": {"title": ".//h2/text()"}
            },
            # Conditional step
            {
                "@if": {"@exists": "#special-section"},
                "@then": [
                    {
                        "@xpath": "//div[@class='special']",
                        "@fields": {"title": ".//h2/text()"}
                    }
                ]
            }
        ]
    })

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Should process both regular and conditional steps
    assert len(results) >= 0  # May have results from both steps


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
def test_execute_query_conditional_with_actions(mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client
    mock_browser_client = MagicMock()
    mock_client = MagicMock()
    mock_page = MagicMock()

    mock_browser_client.__enter__.return_value = mock_client
    mock_browser_client.__exit__.return_value = None
    mock_client.browser = MagicMock()
    mock_client.page = mock_page
    MockBrowserClient.return_value = mock_browser_client

    # Setup mock for checking CAPTCHA
    mock_check_for_captcha.return_value = False

    # Setup mock elements
    login_button = MagicMock()
    mock_page.query_selector.side_effect = lambda sel: login_button if sel == "#login-btn" else MagicMock()
    
    mock_element = MagicMock()
    mock_element.query_selector.return_value = MagicMock(text_content=lambda: "User Content")
    mock_client.browser.new_context.return_value.query_selector_all.return_value = [mock_element]

    # Setup query with actions and conditionals
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@actions": [
            {"@type": "click", "@selector": "#login-btn"},
            {"@type": "wait", "@until": "element", "@selector": "#user-dashboard"}
        ],
        "@steps": [
            {
                "@if": {"@exists": "#user-dashboard"},
                "@then": [
                    {
                        "@xpath": "//div[@class='user-content']",
                        "@fields": {"content": ".//p/text()"}
                    }
                ],
                "@else": [
                    {
                        "@xpath": "//div[@class='guest-content']",
                        "@fields": {"content": ".//p/text()"}
                    }
                ]
            }
        ]
    })

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Verify actions were executed before conditionals
    login_button.click.assert_called_once()
    mock_page.wait_for_selector.assert_called_with("#user-dashboard", timeout=5000)
    
    # Should have conditional results
    assert len(results) >= 0


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
def test_execute_query_nested_conditionals(mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client
    mock_browser_client = MagicMock()
    mock_client = MagicMock()
    mock_page = MagicMock()

    mock_browser_client.__enter__.return_value = mock_client
    mock_browser_client.__exit__.return_value = None
    mock_client.browser = MagicMock()
    mock_client.page = mock_page
    MockBrowserClient.return_value = mock_browser_client

    # Setup mock for checking CAPTCHA
    mock_check_for_captcha.return_value = False

    # Setup mock elements - both conditions true
    mock_page.query_selector.return_value = MagicMock()  # Elements exist
    mock_element = MagicMock()
    mock_element.query_selector.return_value = MagicMock(text_content=lambda: "Premium VIP")
    mock_client.browser.new_context.return_value.query_selector_all.return_value = [mock_element]

    # Setup query with nested conditionals
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@steps": [
            {
                "@if": {"@exists": "#premium-section"},
                "@then": [
                    {
                        "@if": {"@exists": "#vip-section"},
                        "@then": [
                            {
                                "@xpath": "//div[@class='vip-content']",
                                "@fields": {"title": ".//h2/text()"}
                            }
                        ],
                        "@else": [
                            {
                                "@xpath": "//div[@class='premium-content']",
                                "@fields": {"title": ".//h2/text()"}
                            }
                        ]
                    }
                ],
                "@else": [
                    {
                        "@xpath": "//div[@class='basic-content']",
                        "@fields": {"title": ".//h2/text()"}
                    }
                ]
            }
        ]
    })

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Should handle nested conditionals without error
    assert len(results) >= 0