from abc import ABC
from typing import Any
from .browser import BrowserClient
from playwright.sync_api import sync_playwright, Playwright


class PlaywrightClient(BrowserClient, ABC):
    """Concrete implementation of BrowserClient using Playwright."""

    def __init__(self, xvfb: bool = False):
        self.playwright: Playwright | None = None
        self.browser = None
        self.page = None
        self.xvfb = xvfb

    def __enter__(self) -> "PlaywrightClient":
        """Initialize Playwright and open the browser when entering the context."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.xvfb)
        self.page = self.browser.new_page()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Ensure resources are properly closed when exiting the context."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def navigate(self, url: str) -> None:
        """Navigate to the given URL."""
        self.page.goto(url)

    def query_selector(self, selector: str) -> Any:
        """Return an element matching the given selector."""
        return self.page.query_selector(selector)

    def close(self) -> None:
        self.browser.close()
        self.playwright.stop()
