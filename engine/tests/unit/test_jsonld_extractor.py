"""
Tests for the JSON-LD Extractor Plugin.
"""

import pytest
from unittest.mock import MagicMock

from engine.web_engine.plugins.jsonld_extractor import JsonLdExtractorProcessor
from engine.web_engine.models import JsonLdStep, ExtractStep


class TestJsonLdExtractorProcessor:
    
    def test_can_handle_jsonld_step(self):
        processor = JsonLdExtractorProcessor()
        jsonld_step = JsonLdStep(**{
            "@schema": "Product",
            "@fields": ["name", "price"]
        })
        
        assert processor.can_handle(jsonld_step) is True
    
    def test_cannot_handle_extract_step(self):
        processor = JsonLdExtractorProcessor()
        extract_step = ExtractStep(**{
            "@xpath": "//div",
            "@fields": {"title": "text()"}
        })
        
        assert processor.can_handle(extract_step) is False
    
    def test_get_supported_step_types(self):
        processor = JsonLdExtractorProcessor()
        assert processor.get_supported_step_types() == ["JsonLdStep"]
    
    def test_priority_setting(self):
        processor = JsonLdExtractorProcessor()
        assert processor.priority == 25  # Higher precedence than most processors
    
    def test_extract_product_json_ld(self):
        processor = JsonLdExtractorProcessor()
        
        # Mock page with JSON-LD script
        page = MagicMock()
        script_element = MagicMock()
        script_element.text_content.return_value = '''
        {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": "Executive Anvil",
            "image": "anvil.jpg",
            "description": "Heavy duty anvil",
            "brand": {
                "@type": "Brand",
                "name": "ACME"
            },
            "offers": {
                "@type": "Offer",
                "price": "119.99",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        }
        '''
        page.query_selector_all.return_value = [script_element]
        
        jsonld_step = JsonLdStep(**{
            "@schema": "Product",
            "@fields": ["name", "description", "offers"]
        })
        
        results = processor.execute(MagicMock(), page, jsonld_step)
        
        assert len(results) == 1
        result = results[0]
        assert result["name"] == "Executive Anvil"
        assert result["description"] == "Heavy duty anvil"
        assert "offers" in result
        assert result["offers"]["price"] == "119.99"
    
    def test_extract_all_schemas(self):
        processor = JsonLdExtractorProcessor()
        
        # Mock page with multiple JSON-LD scripts
        page = MagicMock()
        script1 = MagicMock()
        script1.text_content.return_value = '''
        {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": "Test Product"
        }
        '''
        script2 = MagicMock()
        script2.text_content.return_value = '''
        {
            "@context": "https://schema.org/",
            "@type": "Organization",
            "name": "Test Company"
        }
        '''
        page.query_selector_all.return_value = [script1, script2]
        
        jsonld_step = JsonLdStep(**{
            "@all-schemas": True
        })
        
        results = processor.execute(MagicMock(), page, jsonld_step)
        
        assert len(results) == 2
        # Check that both Product and Organization are included
        types = [r.get("@type") for r in results]
        assert "Product" in types
        assert "Organization" in types
    
    def test_filter_by_schema_type(self):
        processor = JsonLdExtractorProcessor()
        
        # Mock page with multiple schema types
        page = MagicMock()
        script_element = MagicMock()
        script_element.text_content.return_value = '''
        [
            {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": "Test Product"
            },
            {
                "@context": "https://schema.org/",
                "@type": "Organization",
                "name": "Test Company"
            }
        ]
        '''
        page.query_selector_all.return_value = [script_element]
        
        jsonld_step = JsonLdStep(**{
            "@schema": "Product"
        })
        
        results = processor.execute(MagicMock(), page, jsonld_step)
        
        assert len(results) == 1
        assert results[0]["@type"] == "Product"
        assert results[0]["name"] == "Test Product"
    
    def test_handle_graph_structure(self):
        processor = JsonLdExtractorProcessor()
        
        # Mock page with @graph structure
        page = MagicMock()
        script_element = MagicMock()
        script_element.text_content.return_value = '''
        {
            "@context": "https://schema.org/",
            "@graph": [
                {
                    "@type": "Product",
                    "name": "Product 1"
                },
                {
                    "@type": "Product", 
                    "name": "Product 2"
                }
            ]
        }
        '''
        page.query_selector_all.return_value = [script_element]
        
        jsonld_step = JsonLdStep(**{
            "@schema": "Product",
            "@fields": ["name"]
        })
        
        results = processor.execute(MagicMock(), page, jsonld_step)
        
        assert len(results) == 2
        assert results[0]["name"] == "Product 1"
        assert results[1]["name"] == "Product 2"
    
    def test_no_jsonld_scripts_found(self):
        processor = JsonLdExtractorProcessor()
        
        # Mock page with no JSON-LD scripts
        page = MagicMock()
        page.query_selector_all.return_value = []
        
        jsonld_step = JsonLdStep(**{
            "@schema": "Product"
        })
        
        results = processor.execute(MagicMock(), page, jsonld_step)
        
        assert len(results) == 0
    
    def test_invalid_json_handling(self):
        processor = JsonLdExtractorProcessor()
        
        # Mock page with invalid JSON
        page = MagicMock()
        script_element = MagicMock()
        script_element.text_content.return_value = "{ invalid json }"
        page.query_selector_all.return_value = [script_element]
        
        jsonld_step = JsonLdStep(**{
            "@schema": "Product"
        })
        
        results = processor.execute(MagicMock(), page, jsonld_step)
        
        assert len(results) == 0
    
    def test_clean_value_nested_objects(self):
        processor = JsonLdExtractorProcessor()
        
        # Test cleaning of nested objects
        test_value = {
            "@type": "Offer",
            "price": "99.99",
            "availability": "InStock",
            "@context": "https://schema.org/"
        }
        
        cleaned = processor._clean_value(test_value)
        
        # Should keep @type but remove @context
        assert cleaned["@type"] == "Offer"
        assert cleaned["price"] == "99.99"
        assert "@context" not in cleaned
    
    def test_schema_matching_with_urls(self):
        processor = JsonLdExtractorProcessor()
        
        # Mock page with schema.org URLs
        page = MagicMock()
        script_element = MagicMock()
        script_element.text_content.return_value = '''
        {
            "@context": "https://schema.org/",
            "@type": "https://schema.org/Product",
            "name": "URL Type Product"
        }
        '''
        page.query_selector_all.return_value = [script_element]
        
        jsonld_step = JsonLdStep(**{
            "@schema": "Product",
            "@fields": ["name"]
        })
        
        results = processor.execute(MagicMock(), page, jsonld_step)
        
        assert len(results) == 1
        assert results[0]["name"] == "URL Type Product"