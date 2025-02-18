import logging
from typing import Dict, Optional, Any
from .base.extractor import BaseExtractor, BaseValueExtractor, ValueExtractorFactory

# Set up the logger
logger = logging.getLogger(__name__)


class XPathExtractor(BaseExtractor):
    """Handles extraction of data from elements using XPath expressions."""

    def extract_value(self, element: Any, xpath: str, base_url: Optional[str] = None) -> Optional[Any]:
        """
        Extracts a value from an element using the specified XPath, relying on the appropriate extractor
        determined by ValueExtractorFactory.

        Args:
            element: The element from which to extract data.
            xpath: The XPath expression used for extraction.
            base_url: The base URL for resolving relative links (if applicable).

        Returns:
            A single extracted value if only one element is found, or a list of extracted values if multiple elements are found.
            Returns None if no values were found.
        """
        extractor: BaseValueExtractor = ValueExtractorFactory.create_extractor(xpath)

        if extractor is None:
            logger.warning(f"Unsupported XPath format: {xpath}")
            return None

        # Select all matching elements
        target_elements = element.query_selector_all(f"xpath={extractor.xpath}")

        if not target_elements:
            logger.warning(f"No elements found with XPath: {extractor.xpath}")
            return None

        results = []

        for target_element in target_elements:
            try:
                value = extractor.extract(target_element, base_url)
                if value is not None:
                    results.append(value)
            except Exception as e:
                logger.error(f"Error extracting value: {e}")

        # Return a single value if only one result exists, otherwise return the list
        if len(results) == 1:
            return results[0]  # Return the single extracted value
        elif len(results) > 1:
            return results  # Return the list of extracted values
        else:
            return None  # In case no valid values were extracted

    def extract_fields(self, element: Any, fields: Dict[str, str]) -> Dict[str, Any]:
        """
        Extracts multiple fields from an element using XPath expressions.

        Args:
            element: The element from which to extract fields.
            fields: A dictionary where keys are field names and values are their corresponding XPath expressions.

        Returns:
            A dictionary of field names to extracted values.
        """
        result = {}
        for field, xpath in fields.items():
            value = self.extract_value(element, xpath)
            if value is not None:
                result[field] = value
            else:
                logger.warning(f"Field '{field}' not found with XPath: {xpath}")
        return result
