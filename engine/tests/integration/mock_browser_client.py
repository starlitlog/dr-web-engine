from typing import Any
from engine.web_engine.base.browser import BrowserClient
from unittest.mock import MagicMock


class MockBrowserClient(BrowserClient):
    def __init__(self):
        self.page = MagicMock()
        self.browser = MagicMock()
        self.url = "https://example.com"

    def __enter__(self) -> "MockBrowserClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def navigate(self, url: str) -> None:
        self.url = url

    def query_selector(self, selector: str) -> Any:
        print(f"Querying selector: {selector}")  # Debugging

        if selector == ".//div[contains(@class, 'items-baseline')]/div[1]/span[1]/text()":
            return MockElement("Test Name")
        elif selector == ".//div[contains(@class, 'rating')]/span[1]/text()":
            return MockElement("5 stars")
        elif selector == ".//div[contains(@class, 'profile-image')]//img[1]/@src":
            return MockElement("https://example.com/image.jpg")

        print(f"No match for selector: {selector}")
        return None

    def close(self) -> None:
        pass


class MockElement:
    """Mock class to simulate browser elements with text content."""
    def __init__(self, text):
        self.text = text

    def text_content(self):
        return self.text
