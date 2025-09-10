"""
AI-Selector Plugin for DR Web Engine
Translates natural language descriptions to element selections using configurable AI endpoints.
"""

import os
import json
import logging
import hashlib
from typing import Any, List, Dict, Optional
from dataclasses import dataclass
import requests

from ..processors import StepProcessor
from ..models import AiSelectStep

logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """AI API configuration."""
    endpoint: str = os.getenv("AI_SELECTOR_ENDPOINT", "https://api.openai.com/v1/chat/completions")
    api_key: Optional[str] = os.getenv("AI_SELECTOR_API_KEY")
    model: str = os.getenv("AI_SELECTOR_MODEL", "gpt-4o-mini")
    temperature: float = 0.3
    max_tokens: int = 500
    timeout: int = 30


class AISelectorProcessor(StepProcessor):
    """
    Simple AI-powered element selector.
    Converts natural language to XPath selectors using configured AI endpoint.
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        super().__init__()
        self.priority = 35
        self.config = config or AIConfig()
        self.cache = {}  # Simple in-memory cache
        self.logger = logger
    
    def can_handle(self, step: Any) -> bool:
        """Check if this is an AI selection step."""
        return isinstance(step, AiSelectStep)
    
    def get_supported_step_types(self) -> List[str]:
        """Return supported step types."""
        return ["AiSelectStep"]
    
    def execute(self, context: Any, page: Any, step: AiSelectStep) -> List[Any]:
        """Execute AI-powered element selection."""
        try:
            # Generate cache key
            page_structure = self._extract_page_structure(page)
            cache_key = self._generate_cache_key(page.url, step.find, page_structure)
            
            # Check cache
            if cache_key in self.cache:
                self.logger.info(f"Using cached selector for: {step.find}")
                xpath = self.cache[cache_key]
            else:
                # Get AI suggestion
                xpath = self._get_ai_selector(step.find, page_structure)
                if xpath:
                    self.cache[cache_key] = xpath
                    self.logger.info(f"AI generated selector: {xpath}")
                else:
                    self.logger.warning(f"AI couldn't generate selector for: {step.find}")
                    return []
            
            # Execute XPath and extract data
            results = self._execute_xpath(page, xpath, step.max_results)
            
            # If no results and AI was used, try fallback patterns
            if not results and cache_key not in self.cache:
                fallback_xpath = self._fallback_selector(step.find)
                if fallback_xpath and fallback_xpath != xpath:
                    self.logger.info(f"AI selector found no results, trying fallback: {fallback_xpath}")
                    results = self._execute_xpath(page, fallback_xpath, step.max_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"AI selection failed: {e}")
            return []
    
    def _extract_page_structure(self, page: Any) -> str:
        """Extract minimal page structure for context."""
        try:
            # Get a sample of the page structure
            elements = []
            
            # Common important elements
            important_tags = ['h1', 'h2', 'h3', 'title', 'main', 'article', 'section']
            for tag in important_tags:
                els = page.query_selector_all(tag)[:3]  # First 3 of each
                for el in els:
                    text = el.text_content()[:100].strip() if el else ""
                    classes = el.get_attribute("class") or ""
                    elements.append(f"<{tag} class='{classes}'>{text}</{tag}>")
            
            # Sample of elements with common class patterns
            class_patterns = ['price', 'title', 'product', 'content', 'description', 'button']
            for pattern in class_patterns:
                els = page.query_selector_all(f"[class*='{pattern}']")[:2]
                for el in els:
                    tag = el.tag_name if hasattr(el, 'tag_name') else 'div'
                    text = el.text_content()[:100].strip() if el else ""
                    classes = el.get_attribute("class") or ""
                    elements.append(f"<{tag} class='{classes}'>{text}</{tag}>")
            
            # Get meta information
            title = page.title() or ""
            url = page.url
            
            structure = f"""
URL: {url}
Title: {title}

Sample HTML structure:
{chr(10).join(elements[:20])}  # Limit to 20 elements
"""
            return structure
            
        except Exception as e:
            self.logger.warning(f"Failed to extract page structure: {e}")
            return f"URL: {page.url}"
    
    def _generate_cache_key(self, url: str, description: str, structure: str) -> str:
        """Generate cache key."""
        # Include structure hash for cache invalidation when page changes
        content = f"{url}:{description}:{hashlib.md5(structure.encode()).hexdigest()[:8]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_ai_selector(self, description: str, page_structure: str) -> Optional[str]:
        """Get XPath selector from AI."""
        
        # Build prompt
        prompt = f"""Given this web page structure, generate an XPath selector for: "{description}"

{page_structure}

Return ONLY a valid XPath expression, nothing else. Examples:
- //div[@class='price']
- //h1[contains(@class, 'title')]
- //span[contains(text(), '$')]

XPath for "{description}":"""
        
        try:
            if self.config.api_key:
                # Call AI API
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": "You are an expert at writing XPath selectors. Return only valid XPath expressions."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }
                
                response = requests.post(
                    self.config.endpoint,
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    xpath = result['choices'][0]['message']['content'].strip()
                    
                    # Clean up the XPath (remove quotes, explanations, etc.)
                    xpath = xpath.strip('"\'`')
                    if xpath.startswith('xpath:'):
                        xpath = xpath[6:]
                    
                    # Validate it looks like XPath
                    if xpath.startswith('//') or xpath.startswith('./'):
                        return xpath
                    else:
                        self.logger.warning(f"Invalid XPath from AI: {xpath}")
                        return None
                else:
                    self.logger.error(f"AI API error: {response.status_code}, falling back to patterns")
                    return self._fallback_selector(description)
                    
            else:
                # Fallback to simple patterns
                return self._fallback_selector(description)
                
        except Exception as e:
            self.logger.error(f"AI selector generation failed: {e}")
            return self._fallback_selector(description)
    
    def _fallback_selector(self, description: str) -> Optional[str]:
        """Simple fallback selector based on common patterns."""
        desc_lower = description.lower()
        
        # Common patterns
        patterns = {
            "price": "//span[contains(@class, 'price')] | //div[contains(@class, 'price')] | //*[contains(text(), '$')]",
            "title": "//h1 | //h2[@class='title'] | //div[contains(@class, 'title')] | //h3//a",
            "button": "//button | //a[contains(@class, 'btn')] | //input[@type='submit']",
            "image": "//img[contains(@class, 'product')] | //img[contains(@class, 'main')] | //img",
            "description": "//div[contains(@class, 'description')] | //p[contains(@class, 'desc')]",
            "review": "//div[contains(@class, 'review')] | //div[contains(@class, 'comment')]",
            "rating": "//span[contains(@class, 'rating')] | //div[contains(@class, 'star')]",
            "author": "//span[contains(@class, 'author')] | //small[contains(@class, 'author')] | //div[contains(@class, 'byline')]",
            "date": "//time | //span[contains(@class, 'date')] | //div[contains(@class, 'published')]",
            "content": "//article | //main | //div[contains(@class, 'content')] | //p",
            "text": "//span[contains(@class, 'text')] | //div[contains(@class, 'text')] | //p",
            "quote": "//div[contains(@class, 'quote')] | //blockquote | //span[contains(@class, 'text')]",
            "link": "//a[@href] | //a[contains(@class, 'link')] | //h1/parent::a | //h2/parent::a | //h3/parent::a | //h4/parent::a | //h5/parent::a | //h6/parent::a",
            "headline": "//h1 | //h2 | //h3 | //*[contains(@class, 'headline')]",
            "snippet": "//p | //div[contains(@class, 'snippet')] | //span[contains(@class, 'description')]"
        }
        
        # Find best matching pattern
        for key, xpath in patterns.items():
            if key in desc_lower:
                self.logger.info(f"Using fallback pattern for '{key}'")
                return xpath
        
        # Check for compound descriptions
        if "quote" in desc_lower and "text" in desc_lower:
            return "//span[contains(@class, 'text')] | //div[contains(@class, 'quote')]//span"
        elif "author" in desc_lower and "name" in desc_lower:
            return "//small[contains(@class, 'author')] | //span[contains(@class, 'author')]"
        
        # Generic fallback - get any text content
        return "//*[text() and not(self::script) and not(self::style)]"
    
    def _execute_xpath(self, page: Any, xpath: str, max_results: int) -> List[Dict]:
        """Execute XPath and return results."""
        results = []
        
        try:
            elements = page.query_selector_all(f"xpath={xpath}")
            
            for i, elem in enumerate(elements[:max_results]):
                result = {}
                
                # Extract text
                text = elem.text_content().strip() if elem else ""
                if text:
                    result["text"] = text
                
                # Extract common attributes
                if elem.get_attribute("href"):
                    result["url"] = elem.get_attribute("href")
                if elem.get_attribute("src"):
                    result["image"] = elem.get_attribute("src")
                if elem.get_attribute("alt"):
                    result["alt"] = elem.get_attribute("alt")
                if elem.get_attribute("title"):
                    result["title"] = elem.get_attribute("title")
                
                # Add metadata
                result["xpath_used"] = xpath
                result["index"] = i
                
                if result.get("text") or result.get("url") or result.get("image"):
                    results.append(result)
            
            self.logger.info(f"Found {len(results)} elements with XPath: {xpath}")
            
        except Exception as e:
            self.logger.error(f"XPath execution failed: {e}")
        
        return results


# Simple configuration helper
def configure_ai_selector(
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> AIConfig:
    """
    Configure AI selector with custom settings.
    
    Examples:
        # OpenAI
        config = configure_ai_selector(
            endpoint="https://api.openai.com/v1/chat/completions",
            api_key="sk-...",
            model="gpt-3.5-turbo"
        )
        
        # Local Ollama
        config = configure_ai_selector(
            endpoint="http://localhost:11434/api/chat",
            model="llama2"
        )
        
        # Custom OpenAI-compatible endpoint
        config = configure_ai_selector(
            endpoint="https://my-ai-service.com/v1/chat/completions",
            api_key="my-key",
            model="custom-model"
        )
    """
    config = AIConfig()
    
    if endpoint:
        config.endpoint = endpoint
    if api_key:
        config.api_key = api_key
    if model:
        config.model = model
    
    return config