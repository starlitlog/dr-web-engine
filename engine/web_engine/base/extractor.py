from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse
import logging

# Set up the logger
logger = logging.getLogger(__name__)


# Define the base abstract extractor class
class BaseExtractor(ABC):
    @abstractmethod
    def extract_value(self, element: Any, xpath: str, base_url: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    def extract_fields(self, element: Any, fields: Dict[str, str]) -> Dict[str, Any]:
        pass


# Base Value Extractor Class
class BaseValueExtractor(ABC):
    def __init__(self, xpath: str):
        self.xpath = xpath

    @abstractmethod
    def extract(self, target_element: Any, base_url: Optional[str] = None) -> Optional[str]:
        pass


class HrefValueExtractor(BaseValueExtractor):
    def extract(self, target_element: Any, base_url: Optional[str] = None) -> Optional[str]:
        value = target_element.get_attribute('href')
        if value and base_url and not bool(urlparse(value).netloc):
            value = urljoin(base_url, value)
            logger.debug(f"Normalized relative URL -> {value}")
        return value


class TextValueExtractor(BaseValueExtractor):
    def extract(self, target_element: Any, base_url: Optional[str] = None) -> Optional[str]:
        return target_element.text_content().strip()


class NormalizeSpaceValueExtractor(BaseValueExtractor):
    def extract(self, target_element: Any, base_url: Optional[str] = None) -> Optional[str]:
        return " ".join(target_element.text_content().split())


class SrcValueExtractor(BaseValueExtractor):
    def extract(self, target_element: Any, base_url: Optional[str] = None) -> Optional[str]:
        return target_element.get_attribute('src')


class AltValueExtractor(BaseValueExtractor):
    def extract(self, target_element: Any, base_url: Optional[str] = None) -> Optional[str]:
        return target_element.get_attribute('alt')


class ValueExtractorFactory:
    @staticmethod
    def create_extractor(xpath: str) -> Optional[BaseValueExtractor]:
        """
        Parses an XPath expression and returns an appropriate extractor class instance.
        """
        if xpath.endswith("/text()"):
            cleaned_xpath = xpath[:-7]
            return TextValueExtractor(cleaned_xpath)
        elif xpath.endswith("/@href"):
            cleaned_xpath = xpath[:-6]
            return HrefValueExtractor(cleaned_xpath)
        elif xpath.endswith("/@src"):
            cleaned_xpath = xpath[:-5]
            return SrcValueExtractor(cleaned_xpath)
        elif xpath.endswith("/@alt"):
            cleaned_xpath = xpath[:-5]
            return AltValueExtractor(cleaned_xpath)
        elif xpath.endswith("/normalize-space()"):
            cleaned_xpath = xpath[:-18]
            return NormalizeSpaceValueExtractor(cleaned_xpath)
        else:
            logger.warning(f"Unsupported XPath format: {xpath}")
            return None
