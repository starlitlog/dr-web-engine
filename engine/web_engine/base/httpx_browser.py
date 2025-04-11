from abc import ABC
from typing import Any
import httpx
from parsel import Selector
from .browser import BrowserClient


class HttpxClient(BrowserClient, ABC):
    """
    Alternative implementation of BrowserClient using httpx and parsel for fast HTML
    extraction with XPath support."""

    def __init__(self):
        self.client = httpx.Client()
        self.response = None
        self.selector = None  # A `parsel.Selector` instance for querying DOM

    def __enter__(self) -> "HttpxClient":
        """Initialize the HTTP client when entering the context."""
        self.client = httpx.Client()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Ensure resources are properly closed when exiting the context."""
        self.client.close()

    def navigate(self, url: str) -> None:
        """Fetch the raw HTML of the given URL without rendering JavaScript."""
        self.response = self.client.get(url)
        self.selector = Selector(self.response.text)

    def query_selector(self, selector: str) -> Any:
        """Return an element matching the given XPath selector."""
        return self.selector.xpath(selector).get()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
