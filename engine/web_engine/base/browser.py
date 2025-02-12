from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BrowserClient(ABC):
    """Abstract base class for browser clients."""

    @abstractmethod
    def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        pass

    @abstractmethod
    def query_selector(self, selector: str) -> Any:
        """Query the DOM for an element matching the selector."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the browser."""
        pass
