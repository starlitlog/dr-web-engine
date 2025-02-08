import pytest
from unittest.mock import MagicMock
from web_cli.web_engine.engine import execute_query, extract_fields
from web_cli.web_engine.models import ExtractionQuery, ExtractStep, PaginationSpec


@pytest.fixture
def mock_page():
    """Mock a Playwright page object."""
    page = MagicMock()
    page.query_selector_all.return_value = [MagicMock()]
    return page


def test_extract_fields(mock_page):
    """Test field extraction from an element."""
    element = MagicMock()
    element.query_selector.return_value = MagicMock(text_content=lambda: "Test Value")
    fields = {"test_field": ".//test"}
    result = extract_fields(element, fields)
    assert result == {"test_field": "Test Value"}


def test_execute_query(mock_page):
    """Test query execution with a mock Playwright browser."""
    query = ExtractionQuery(
        url="https://example.com",
        steps=[ExtractStep(xpath="//div", fields={"field": ".//span"})]
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("playwright.sync_api.sync_playwright", lambda: MagicMock())
        results = execute_query(query)
    assert isinstance(results, list)


def test_pagination(mock_page):
    """Test pagination handling."""
    query = ExtractionQuery(
        url="https://example.com",
        steps=[ExtractStep(xpath="//div", fields={"field": ".//span"})],
        pagination=PaginationSpec(xpath="//a[@id='next']", limit=2)
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("playwright.sync_api.sync_playwright", lambda: MagicMock())
        results = execute_query(query)
    assert isinstance(results, list)