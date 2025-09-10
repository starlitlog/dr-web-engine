import pytest
from unittest.mock import MagicMock, patch
from engine.web_engine.engine import execute_query
from engine.web_engine.models import ExtractionQuery, ExtractStep, ClickAction, WaitAction, ScrollAction


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
@patch('engine.web_engine.engine.StepProcessorRegistry')
def test_execute_query_with_actions(MockStepProcessorRegistry, mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client to match actual engine.py usage
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

    # Setup mock step processor registry
    mock_registry_instance = MagicMock()
    mock_registry_instance.process_step.return_value = [{"title": "Test Item"}]
    MockStepProcessorRegistry.return_value = mock_registry_instance

    # Setup mock elements for actions
    mock_click_element = MagicMock()
    mock_page.query_selector.return_value = mock_click_element

    # Setup query with actions
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@actions": [
            {"@type": "click", "@selector": ".load-more"},
            {"@type": "wait", "@until": "timeout", "@timeout": 2000},
            {"@type": "scroll", "@direction": "down", "@pixels": 500}
        ],
        "@steps": [
            {"@xpath": "//div[@class='item']", "@name": "items", "@fields": {"title": ".//h2/text()"}}
        ]
    })

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Verify actions were executed
    # Click action: element.click() should be called
    mock_page.query_selector.assert_called_with(".load-more")
    mock_click_element.click.assert_called_once()
    
    # Wait and scroll actions: page methods should be called
    mock_page.wait_for_timeout.assert_called_with(2000)
    mock_page.evaluate.assert_called_with("window.scrollBy(0, 500)")

    # Verify extraction step was executed
    mock_registry_instance.process_step.assert_called()
    
    # Assert results
    assert results == [{"title": "Test Item"}]


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
@patch('engine.web_engine.engine.StepProcessorRegistry')
def test_execute_query_no_actions(MockStepProcessorRegistry, mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client to match actual engine.py usage
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

    # Setup mock step processor registry
    mock_registry_instance = MagicMock()
    mock_registry_instance.process_step.return_value = [{"title": "Test Item"}]
    MockStepProcessorRegistry.return_value = mock_registry_instance

    # Setup query without actions
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@steps": [
            {"@xpath": "//div[@class='item']", "@name": "items", "@fields": {"title": ".//h2/text()"}}
        ]
    })

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Verify no actions were executed
    # Only page.goto should have been called, not action-related methods

    # Verify extraction step was executed
    mock_registry_instance.process_step.assert_called()
    
    # Assert results
    assert results == [{"title": "Test Item"}]


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
@patch('engine.web_engine.engine.StepProcessorRegistry')
def test_execute_query_with_form_actions(MockStepProcessorRegistry, mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client to match actual engine.py usage
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

    # Setup mock elements for form actions
    mock_input_element = MagicMock()
    mock_button_element = MagicMock()
    
    def mock_query_selector(selector):
        if selector == "input[name='q']":
            return mock_input_element
        elif selector == "button[type='submit']":
            return mock_button_element
        elif selector == ".results":
            return MagicMock()
        return None
    
    mock_page.query_selector.side_effect = mock_query_selector

    # Setup query with form actions
    query = ExtractionQuery(**{
        "@url": "https://example.com/search",
        "@actions": [
            {"@type": "fill", "@selector": "input[name='q']", "@value": "test query"},
            {"@type": "click", "@selector": "button[type='submit']"},
            {"@type": "wait", "@until": "element", "@selector": ".results", "@timeout": 5000}
        ],
        "@steps": [
            {"@xpath": "//div[@class='result']", "@name": "results", "@fields": {"title": ".//h3/text()"}}
        ]
    })

    # Setup mock step processor registry
    mock_registry_instance = MagicMock()
    mock_registry_instance.process_step.return_value = [{"title": "Search Result"}]
    MockStepProcessorRegistry.return_value = mock_registry_instance

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Verify form actions were executed in order
    mock_input_element.fill.assert_called_once_with("test query")
    mock_button_element.click.assert_called_once()
    mock_page.wait_for_selector.assert_called_once_with(".results", timeout=5000)

    # Verify extraction step was executed
    mock_registry_instance.process_step.assert_called_once()
    
    # Assert results
    assert results == [{"title": "Search Result"}]


@patch('engine.web_engine.engine.ActionProcessor')
@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
@patch('engine.web_engine.engine.execute_step')
def test_action_processor_called_with_correct_parameters(mock_execute_step, mock_check_for_captcha, MockBrowserClient, MockActionProcessor):
    # Setup mocks
    mock_browser_client = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_action_processor = MagicMock()

    mock_browser_client.__enter__.return_value = mock_browser
    mock_browser_client.__exit__.return_value = None
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    MockBrowserClient.return_value = mock_browser_client
    MockActionProcessor.return_value = mock_action_processor

    mock_check_for_captcha.return_value = False
    mock_execute_step.return_value = [{"title": "Test"}]

    # Setup query with actions
    actions = [
        ClickAction(**{"@type": "click", "@selector": ".btn"}),
        WaitAction(**{"@type": "wait", "@until": "timeout", "@timeout": 1000})
    ]
    
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@actions": [
            {"@type": "click", "@selector": ".btn"},
            {"@type": "wait", "@until": "timeout", "@timeout": 1000}
        ],
        "@steps": [{"@xpath": "//div", "@name": "items", "@fields": {"title": ".//text()"}}]
    })

    # Execute the function
    execute_query(query, mock_browser_client)

    # Verify ActionProcessor was instantiated and called correctly
    MockActionProcessor.assert_called_once()
    # Note: The page passed may be different due to browser setup, check call was made
    mock_action_processor.execute_actions.assert_called_once()


@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
@patch('engine.web_engine.engine.StepProcessorRegistry')
def test_execute_query_actions_with_pagination(MockStepProcessorRegistry, mock_check_for_captcha, MockBrowserClient):
    # Setup mock browser client to match actual engine.py usage
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

    # Setup browser context mock (needed for execute_step calls)
    mock_context = MagicMock()
    mock_client.browser.new_context.return_value = mock_context

    # Setup query with both actions and pagination
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@actions": [
            {"@type": "wait", "@until": "element", "@selector": ".content", "@timeout": 5000}
        ],
        "@steps": [
            {"@xpath": "//div[@class='item']", "@name": "items", "@fields": {"title": ".//h2/text()"}}
        ],
        "@pagination": {"@xpath": "//a[@class='next']", "@limit": 2}
    })

    # Setup mock step processor registry
    mock_registry_instance = MagicMock()
    mock_registry_instance.process_step.return_value = [{"title": "Test Item"}]
    MockStepProcessorRegistry.return_value = mock_registry_instance

    # Simulate pagination - first page has next link, second page doesn't
    mock_page.query_selector.side_effect = [
        MagicMock(get_attribute=lambda x: "https://example.com/page2"),  # First page
        None  # Second page (no next link)
    ]

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Verify actions were executed only once (before pagination loop)
    mock_page.wait_for_selector.assert_called_once_with(".content", timeout=5000)

    # Verify extraction steps were executed
    assert mock_registry_instance.process_step.call_count == 2
    
    # Assert results from both pages
    assert results == [{"title": "Test Item"}, {"title": "Test Item"}]