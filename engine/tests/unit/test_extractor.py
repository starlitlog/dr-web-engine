import unittest
from unittest.mock import MagicMock, patch
from engine.web_engine.engine import XPathExtractor  # Update the import path as needed


class TestXPathExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = XPathExtractor()
        self.mock_element = MagicMock()

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_text(self, mock_logger):
        # Mocking query_selector_all to simulate returning one element
        mock_target = MagicMock()
        mock_target.text_content.return_value = " Test Text "
        self.mock_element.query_selector_all.return_value = [mock_target]  # Make it return a list for one item
        result = self.extractor.extract_value(self.mock_element, "//div/text()", "text")
        self.assertEqual(result, "Test Text")  # Expecting direct value

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_href_absolute(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "https://example.com/page"
        self.mock_element.query_selector_all.return_value = [mock_target]  # Simulate single target
        result = self.extractor.extract_value(self.mock_element, "//a/@href", "href")
        self.assertEqual(result, "https://example.com/page")  # Expecting direct value

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_href_relative(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "/relative/path"
        self.mock_element.query_selector_all.return_value = [mock_target]
        result = self.extractor.extract_value(self.mock_element, "//a/@href", "https://example.com")
        self.assertEqual(result, "https://example.com/relative/path")  # Expecting direct value

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_normalize_space(self, mock_logger):
        mock_target = MagicMock()
        mock_target.text_content.return_value = "  Hello   World  "
        self.mock_element.query_selector_all.return_value = [mock_target]
        result = self.extractor.extract_value(self.mock_element, "//p/normalize-space()", "normalize-space")
        self.assertEqual(result, "Hello World")  # Expecting direct value

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_src(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "https://example.com/image.jpg"
        self.mock_element.query_selector_all.return_value = [mock_target]
        result = self.extractor.extract_value(self.mock_element, "//img/@src", "src")
        self.assertEqual(result, "https://example.com/image.jpg")  # Expecting direct value

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_alt(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "Alt Text"
        self.mock_element.query_selector_all.return_value = [mock_target]
        result = self.extractor.extract_value(self.mock_element, "//img/@alt", "alt")
        self.assertEqual(result, "Alt Text")  # Expecting direct value

    @patch("engine.web_engine.engine.logger")
    def test_extract_fields(self, mock_logger):
        # Mocking the query_selector_all to return a list of MagicMock objects
        mock_image_element = MagicMock()
        mock_image_element.get_attribute.return_value = "https://example.com/image.jpg"

        # When first called, it returns one element followed by the image element.
        self.mock_element.query_selector_all.side_effect = [
            [MagicMock(text_content=lambda: "Field1 Value")],  # One value as a list
            [mock_image_element]  # Another list for image
        ]

        fields = {"title": "//h1/text()", "image": "//img/@src"}
        result = self.extractor.extract_fields(self.mock_element, fields)

        # Adjust expected results
        self.assertEqual(result, {"title": "Field1 Value", "image": "https://example.com/image.jpg"})


if __name__ == "__main__":
    unittest.main()
