import pytest
import os
from unittest.mock import patch
from engine.web_engine.engine import execute_query
from engine.web_engine.parsers import parse_json5
from .mock_browser_client import MockBrowserClient


@pytest.fixture
def mock_browser_client():
    return MockBrowserClient()


def test_execute_query_integration(mock_browser_client):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    query_file_path = os.path.join(test_dir, 'query.json5')

    query_data = parse_json5(query_file_path)

    with patch('engine.web_engine.engine.check_for_captcha', return_value=False):
        results = execute_query(query_data, mock_browser_client)
        print(results)

    expected_results = [
       # {"full_name": "Test Name", "ratings": "5 stars", "image_url": "https://example.com/image.jpg"}
    ]
    # TODO: Fix the test

    assert results == expected_results
