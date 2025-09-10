import pytest
from unittest.mock import MagicMock, patch
from engine.web_engine.engine import extract_fields, check_for_captcha, execute_step, execute_query
from engine.web_engine.models import ExtractionQuery, ExtractStep, PaginationSpec
from engine.web_engine.base.browser import BrowserClient


# 1. Test `extract_fields` function
def test_extract_fields():
    element = MagicMock()
    element.query_selector.return_value = MagicMock(text_content=lambda: "Test Value",
                                                    get_attribute=lambda x: "http://example.com/image.jpg")

    fields = {"test_field": ".//test", "image_url": ".//img/@src"}

    result = extract_fields(element, fields)

    assert result == {
        "test_field": "Test Value",
        "image_url": "http://example.com/image.jpg"
    }


# 2. Test `check_for_captcha` function
def test_check_for_captcha():
    # Create a MagicMock object to represent the page
    page = MagicMock()

    # Patch the query_selector method on the page object
    with patch.object(page, 'query_selector') as mock_query_selector:
        # Simulate CAPTCHA detected
        mock_query_selector.return_value = MagicMock()

        result = check_for_captcha(page)

        # Assert that CAPTCHA was detected
        assert result is True

        # Simulate no CAPTCHA
        mock_query_selector.return_value = None

        result = check_for_captcha(page)

        # Assert that no CAPTCHA was detected
        assert result is False


@patch('engine.web_engine.engine.XPathExtractor')
@patch('engine.web_engine.engine.BrowserClient')
def test_execute_step(MockBrowserClient, MockExtractor):
    # Setup mock browser client
    mock_browser_client = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    # Mock method calls
    mock_browser_client.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    MockBrowserClient.return_value = mock_browser_client

    # Setup mock extractor
    mock_step = ExtractStep(
        **{"@xpath": "//div[contains(@class, 'test-class')]",
           "@name": "FieldName",
           "@fields": {"field1": ".//text()", "field2": ".//img/@src"}
           }
    )
    mock_elements = [MagicMock()]
    mock_page.query_selector_all.return_value = mock_elements
    mock_extractor = MagicMock()
    mock_extractor.extract_fields.return_value = {"field1": "Value", "field2": "http://example.com/image.jpg"}
    MockExtractor.return_value = mock_extractor

    # Call the function
    results = execute_step(mock_context, mock_page, mock_step)

    # Check that the extractor was called correctly
    mock_extractor.extract_fields.assert_called_with(mock_elements[0], mock_step.fields)

    # Validate the results
    assert results == [{"field1": "Value", "field2": "http://example.com/image.jpg"}]


# 4. Test `execute_query` function
@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
@patch('engine.web_engine.engine.StepProcessorRegistry')
def test_execute_query(MockStepProcessorRegistry, mock_check_for_captcha, MockBrowserClient):
    # Setup mock for BrowserClient and page
    mock_browser_client = MagicMock()
    mock_browser = MagicMock()
    mock_page = MagicMock()

    mock_browser_client.__enter__.return_value = mock_browser
    mock_browser_client.__exit__.return_value = None
    mock_browser.browser = mock_browser
    mock_browser.page = mock_page
    mock_browser.new_context.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page
    MockBrowserClient.return_value = mock_browser_client

    # Setup mock for checking CAPTCHA
    mock_check_for_captcha.return_value = False

    # Setup mock step processor registry
    mock_registry_instance = MagicMock()
    mock_registry_instance.process_step.return_value = [{"field1": "Test Value"}]
    MockStepProcessorRegistry.return_value = mock_registry_instance

    # Setup mock query data
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@name": "FieldName",
        "@steps": [ExtractStep(**{"@xpath": "//div", "@fields": {"field1": ".//span"}})]
     }
    )

    # Execute the function
    results = execute_query(query, mock_browser_client)

    # Assert results
    assert results == [{"field1": "Test Value"}]
    mock_registry_instance.process_step.assert_called()


# 5. Test pagination in `execute_query`
@patch('engine.web_engine.engine.BrowserClient')
@patch('engine.web_engine.engine.check_for_captcha')
@patch('engine.web_engine.engine.StepProcessorRegistry')
def test_execute_query_pagination(MockStepProcessorRegistry, mock_check_for_captcha, MockBrowserClient):
    # Setup mock for BrowserClient and browser
    mock_browser_client = MagicMock()
    mock_browser = MagicMock()
    mock_browser_client.__enter__.return_value = mock_browser
    mock_browser_client.__exit__.return_value = None

    # Mock context and page
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_browser.browser = mock_browser
    mock_browser.page = mock_page
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    MockBrowserClient.return_value = mock_browser_client

    # Setup mock for checking CAPTCHA
    mock_check_for_captcha.return_value = False

    # Setup mock step processor registry
    mock_registry_instance = MagicMock()
    mock_registry_instance.process_step.return_value = [{"field1": "Test Value"}]
    MockStepProcessorRegistry.return_value = mock_registry_instance

    # Setup query with pagination
    query = ExtractionQuery(**{
        "@url": "https://example.com",
        "@steps": [ExtractStep(**{"@xpath": "//div", "@name": "FieldName", "@fields": {"field1": ".//span"}})],
        "@pagination": PaginationSpec(**{"@xpath": "//a[@class='next']", "@limit": 2})
    })

    # Simulate the first page with pagination
    mock_page.query_selector.return_value = MagicMock(get_attribute=lambda x: "https://example.com/page2")

    # Execute the function
    results = execute_query(query, mock_browser_client)

    print("Actual results:", results)
    print("Expected results:", [{"field1": "Test Value"}])

    # Assert that pagination was handled  
    assert results == [{'field1': 'Test Value'}, {'field1': 'Test Value'}]
    mock_registry_instance.process_step.assert_called()

