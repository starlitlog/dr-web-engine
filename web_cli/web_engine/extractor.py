import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class XPathExtractor:
    """Handles extraction of data from elements using XPath expressions."""

    @staticmethod
    def parse_xpath(xpath: str) -> tuple:
        """
        Parses an XPath expression to detect functions like /text(), @href, @src, or normalize-space().
        Returns a tuple of (cleaned_xpath, extraction_method).
        """
        if xpath.endswith("/text()"):
            return xpath[:-7], "text"
        elif xpath.endswith("/@href"):
            return xpath[:-6], "href"
        elif xpath.endswith("/@src"):
            return xpath[:-5], "src"
        elif xpath.endswith("/normalize-space()"):
            return xpath[:-18], "normalize-space"
        else:
            return xpath, None

    @staticmethod
    def extract_value(element, xpath: str, extraction_method: Optional[str] = None):
        """
        Extracts a value from an element using the specified XPath and extraction method.
        Supports normalize-space() for trimming and collapsing whitespace.
        """
        target_element = element.query_selector(f"xpath={xpath}")
        if not target_element:
            logger.warning(f"Element not found with XPath: {xpath}")
            return None

        if extraction_method == "text":
            return target_element.text_content().strip()
        elif extraction_method == "href":
            return target_element.get_attribute("href")
        elif extraction_method == "src":
            return target_element.get_attribute("src")
        elif extraction_method == "normalize-space":
            # Use normalize-space() to trim and collapse whitespace
            return " ".join(target_element.text_content().split())
        else:
            # Default to returning the element itself
            return target_element

    def extract_fields(self, element, fields: Dict[str, str]) -> Dict[str, str]:
        """
        Extracts multiple fields from an element using XPath expressions.
        """
        result = {}
        for field, xpath in fields.items():
            cleaned_xpath, extraction_method = self.parse_xpath(xpath)
            value = self.extract_value(element, cleaned_xpath, extraction_method)
            if value is not None:
                result[field] = value
            else:
                logger.warning(f"Field '{field}' not found with XPath: {xpath}")
        return result

