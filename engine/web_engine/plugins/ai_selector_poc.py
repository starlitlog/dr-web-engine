"""
AI-Selector Plugin - Proof of Concept
This is a conceptual implementation showing how AI-powered element selection could work.
NOTE: This requires API keys and model access to function.
"""

import os
import json
import logging
from typing import Any, List, Dict, Optional
from dataclasses import dataclass
import hashlib

from ..processors import StepProcessor
from ..models import BaseModel, Field

logger = logging.getLogger(__name__)


@dataclass
class ElementContext:
    """Context information about an element."""
    html: str
    text: str
    tag: str
    classes: List[str]
    id: Optional[str]
    position: Dict[str, int]  # top, left, width, height
    path: str  # XPath to element


class AiSelectStep(BaseModel):
    """Model for AI-powered element selection."""
    find: str = Field(alias="@find")  # Natural language description
    context_hint: Optional[str] = Field(default=None, alias="@context")
    element_type: Optional[str] = Field(default=None, alias="@type")
    confidence: float = Field(default=0.7, alias="@confidence")
    examples: Optional[List[str]] = Field(default=None, alias="@examples")
    extract: Optional[Dict[str, str]] = Field(default=None, alias="@extract")
    visual: Optional[Dict[str, Any]] = Field(default=None, alias="@visual")
    relationship: Optional[Dict[str, str]] = Field(default=None, alias="@relationship")
    name: Optional[str] = Field(default=None, alias="@name")


class AISelectorProcessor(StepProcessor):
    """
    AI-powered element selector processor.
    Uses natural language to identify and extract elements from web pages.
    """
    
    def __init__(self, provider: str = "openai"):
        super().__init__()
        self.priority = 35  # Higher priority than most processors
        self.provider = provider
        self.cache = {}  # Simple in-memory cache
        
        # Initialize AI provider (mock for POC)
        self._initialize_ai_provider()
    
    def _initialize_ai_provider(self):
        """Initialize the AI model provider."""
        if self.provider == "openai":
            # Would initialize OpenAI client here
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("OpenAI API key not found. AI selector will use mock mode.")
                self.mock_mode = True
            else:
                self.mock_mode = False
                # from openai import OpenAI
                # self.client = OpenAI(api_key=self.api_key)
        else:
            self.mock_mode = True
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is an AI selection step."""
        return isinstance(step, AiSelectStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return list of step types this processor supports."""
        return ["AiSelectStep"]
    
    def execute(self, context: Any, page: Any, step: AiSelectStep) -> List[Any]:
        """Execute AI-powered element selection."""
        try:
            self.logger.info(f"AI-selecting elements: {step.find}")
            
            # Generate cache key
            cache_key = self._generate_cache_key(page.url, step.find)
            
            # Check cache first
            if cache_key in self.cache:
                self.logger.info("Using cached AI selection")
                return self.cache[cache_key]
            
            # Extract page context
            page_context = self._extract_page_context(page)
            
            # Get AI selection
            if self.mock_mode:
                selected_elements = self._mock_ai_selection(page, step, page_context)
            else:
                selected_elements = self._ai_select_elements(page, step, page_context)
            
            # Filter by confidence
            confident_elements = [
                elem for elem in selected_elements 
                if elem.get("confidence", 0) >= step.confidence
            ]
            
            # Extract requested fields
            results = self._extract_fields(page, confident_elements, step)
            
            # Cache results
            self.cache[cache_key] = results
            
            self.logger.info(f"AI-selected {len(results)} elements with confidence >= {step.confidence}")
            return results
            
        except Exception as e:
            self.logger.error(f"AI selection failed: {e}")
            # Fallback to empty results or traditional selection
            return []
    
    def _generate_cache_key(self, url: str, description: str) -> str:
        """Generate cache key for AI selections."""
        content = f"{url}:{description}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_page_context(self, page: Any) -> Dict:
        """Extract context from the page for AI analysis."""
        try:
            # Get page HTML structure
            html = page.content()
            
            # Get page title
            title = page.title()
            
            # Get meta description
            meta_desc = page.query_selector("meta[name='description']")
            description = meta_desc.get_attribute("content") if meta_desc else ""
            
            # Identify main content areas
            main_content = page.query_selector("main, #content, .content, article")
            
            # Get structured data if available
            json_ld_scripts = page.query_selector_all('script[type="application/ld+json"]')
            structured_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.text_content())
                    structured_data.append(data)
                except:
                    pass
            
            return {
                "url": page.url,
                "title": title,
                "description": description,
                "has_main": main_content is not None,
                "structured_data": structured_data,
                "html_length": len(html)
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to extract page context: {e}")
            return {"url": page.url}
    
    def _mock_ai_selection(self, page: Any, step: AiSelectStep, context: Dict) -> List[Dict]:
        """Mock AI selection for testing without API access."""
        results = []
        
        # Simple pattern matching for common requests
        find_lower = step.find.lower()
        
        if "price" in find_lower:
            # Look for price-like elements
            selectors = [
                "//span[contains(@class, 'price')]",
                "//div[contains(@class, 'price')]",
                "//*[@itemprop='price']",
                "//span[contains(text(), '$')]",
                "//span[contains(text(), '€')]",
                "//span[contains(text(), '£')]"
            ]
        elif "title" in find_lower or "name" in find_lower:
            selectors = [
                "//h1",
                "//h2[@class='title']",
                "//*[@itemprop='name']",
                "//div[contains(@class, 'title')]",
                "//span[contains(@class, 'product-name')]"
            ]
        elif "image" in find_lower:
            selectors = [
                "//img[contains(@class, 'product')]",
                "//img[contains(@class, 'main')]",
                "//*[@itemprop='image']",
                "//div[contains(@class, 'gallery')]//img"
            ]
        elif "review" in find_lower:
            selectors = [
                "//div[contains(@class, 'review')]",
                "//div[contains(@class, 'comment')]",
                "//*[@itemprop='review']",
                "//article[contains(@class, 'review')]"
            ]
        elif "button" in find_lower:
            selectors = [
                "//button",
                "//input[@type='submit']",
                "//a[contains(@class, 'btn')]",
                "//div[contains(@class, 'button')]"
            ]
        else:
            # Generic content selection
            selectors = [
                "//p",
                "//div[contains(@class, 'content')]",
                "//span[not(@class='hidden')]"
            ]
        
        # Try each selector
        for selector in selectors:
            try:
                elements = page.query_selector_all(f"xpath={selector}")
                for elem in elements[:10]:  # Limit to first 10
                    text = elem.text_content().strip()
                    if text:  # Only include elements with text
                        results.append({
                            "selector": selector,
                            "text": text,
                            "confidence": 0.6,  # Mock confidence
                            "element": elem
                        })
            except:
                continue
        
        # Sort by confidence (mock)
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results[:5]  # Return top 5 matches
    
    def _ai_select_elements(self, page: Any, step: AiSelectStep, context: Dict) -> List[Dict]:
        """
        Use AI to select elements from the page.
        This would integrate with OpenAI, Claude, or other AI providers.
        """
        # This is where the actual AI integration would happen
        # For now, this is a conceptual implementation
        
        prompt = self._build_selection_prompt(step, context)
        
        # Would make API call here
        # response = self.client.chat.completions.create(
        #     model="gpt-4-vision-preview",
        #     messages=[
        #         {"role": "system", "content": "You are an expert at identifying elements on web pages."},
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        
        # For POC, return mock results
        return self._mock_ai_selection(page, step, context)
    
    def _build_selection_prompt(self, step: AiSelectStep, context: Dict) -> str:
        """Build prompt for AI model."""
        prompt = f"""
        Find elements on this webpage that match: "{step.find}"
        
        Page context:
        - URL: {context.get('url')}
        - Title: {context.get('title')}
        - Has main content area: {context.get('has_main')}
        """
        
        if step.context_hint:
            prompt += f"\nAdditional context: {step.context_hint}"
        
        if step.element_type:
            prompt += f"\nElement type: {step.element_type}"
        
        if step.examples:
            prompt += f"\nExamples of content to find: {', '.join(step.examples)}"
        
        prompt += """
        
        Return the XPath selectors for matching elements with confidence scores.
        Format: [{"xpath": "...", "confidence": 0.9, "reason": "..."}, ...]
        """
        
        return prompt
    
    def _extract_fields(self, page: Any, elements: List[Dict], step: AiSelectStep) -> List[Dict]:
        """Extract requested fields from selected elements."""
        results = []
        
        for elem_data in elements:
            if "element" not in elem_data:
                continue
                
            elem = elem_data["element"]
            result = {
                "confidence": elem_data.get("confidence", 0),
                "selector_used": elem_data.get("selector", "ai-selected")
            }
            
            if step.extract:
                # Extract specific fields as requested
                for field_name, field_desc in step.extract.items():
                    # This would use AI to extract specific fields
                    # For now, just get text content
                    result[field_name] = elem.text_content().strip()
            else:
                # Just return the text content
                result["text"] = elem.text_content().strip()
                
                # Try to get common attributes
                if elem.get_attribute("href"):
                    result["url"] = elem.get_attribute("href")
                if elem.get_attribute("src"):
                    result["image"] = elem.get_attribute("src")
                if elem.get_attribute("alt"):
                    result["alt"] = elem.get_attribute("alt")
            
            results.append(result)
        
        return results


# Utility functions for AI selection

def describe_element(element) -> str:
    """Generate natural language description of an element."""
    tag = element.tag_name
    classes = element.get_attribute("class") or ""
    id_attr = element.get_attribute("id") or ""
    text_preview = element.text_content()[:100].strip()
    
    description = f"A {tag} element"
    if id_attr:
        description += f" with id '{id_attr}'"
    if classes:
        description += f" with classes '{classes}'"
    if text_preview:
        description += f" containing text: '{text_preview}...'"
    
    return description


def calculate_element_similarity(description: str, element_desc: str) -> float:
    """
    Calculate similarity between a description and an element.
    This would use embeddings in a real implementation.
    """
    # Simplified similarity for POC
    desc_words = set(description.lower().split())
    elem_words = set(element_desc.lower().split())
    
    if not desc_words or not elem_words:
        return 0.0
    
    intersection = desc_words & elem_words
    union = desc_words | elem_words
    
    return len(intersection) / len(union) if union else 0.0


# Example configuration for AI selector

AI_SELECTOR_CONFIG = {
    "provider": "openai",  # or "claude", "local", "huggingface"
    "model": "gpt-4-vision-preview",
    "temperature": 0.3,  # Lower temperature for more consistent selection
    "max_elements": 50,  # Maximum elements to consider
    "cache_ttl": 3600,  # Cache selections for 1 hour
    "fallback_to_xpath": True,  # Fall back to XPath if AI fails
    "confidence_threshold": 0.7,
    "vision_enabled": True,  # Use vision models for visual descriptions
    "batch_size": 10,  # Process elements in batches
}