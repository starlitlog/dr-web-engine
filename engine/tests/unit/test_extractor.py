import unittest
from unittest.mock import MagicMock, patch
from engine.web_engine.engine import XPathExtractor  # Update the import path as needed


class TestXPathExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = XPathExtractor()
        self.mock_element = MagicMock()

    def test_parse_xpath(self):
        self.assertEqual(self.extractor.parse_xpath("//div/text()"), ("//div", "text"))
        self.assertEqual(self.extractor.parse_xpath("//a/@href"), ("//a", "href"))
        self.assertEqual(self.extractor.parse_xpath("//img/@src"), ("//img", "src"))
        self.assertEqual(self.extractor.parse_xpath("//span/@alt"), ("//span", "alt"))
        self.assertEqual(self.extractor.parse_xpath("//p/normalize-space()"), ("//p", "normalize-space"))
        self.assertEqual(self.extractor.parse_xpath("//div"), ("//div", None))

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_text(self, mock_logger):
        self.mock_element.query_selector.return_value.text_content.return_value = " Test Text "
        result = self.extractor.extract_value(self.mock_element, "//div", "text")
        self.assertEqual(result, "Test Text")

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_href_absolute(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "https://example.com/page"
        self.mock_element.query_selector.return_value = mock_target
        result = self.extractor.extract_value(self.mock_element, "//a", "href")
        self.assertEqual(result, "https://example.com/page")

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_href_relative(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "/relative/path"
        self.mock_element.query_selector.return_value = mock_target
        result = self.extractor.extract_value(self.mock_element, "//a", "href", "https://example.com")
        self.assertEqual(result, "https://example.com/relative/path")

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_normalize_space(self, mock_logger):
        self.mock_element.query_selector.return_value.text_content.return_value = "  Hello   World  "
        result = self.extractor.extract_value(self.mock_element, "//p", "normalize-space")
        self.assertEqual(result, "Hello World")

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_src(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "https://example.com/image.jpg"
        self.mock_element.query_selector.return_value = mock_target
        result = self.extractor.extract_value(self.mock_element, "//img", "src")
        self.assertEqual(result, "https://example.com/image.jpg")

    @patch("engine.web_engine.engine.logger")
    def test_extract_value_alt(self, mock_logger):
        mock_target = MagicMock()
        mock_target.get_attribute.return_value = "Alt Text"
        self.mock_element.query_selector.return_value = mock_target
        result = self.extractor.extract_value(self.mock_element, "//img", "alt")
        self.assertEqual(result, "Alt Text")

    @patch("engine.web_engine.engine.logger")
    def test_extract_fields(self, mock_logger):
        self.mock_element.query_selector.side_effect = [
            MagicMock(text_content=lambda: "Field1 Value"),
            MagicMock(get_attribute=lambda x: "https://example.com/image.jpg")
        ]
        fields = {"title": "//h1/text()", "image": "//img/@src"}
        result = self.extractor.extract_fields(self.mock_element, fields)
        self.assertEqual(result, {"title": "Field1 Value", "image": "https://example.com/image.jpg"})

if __name__ == "__main__":
    unittest.main()
