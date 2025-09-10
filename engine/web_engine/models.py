from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Union, Literal, Any
from urllib.parse import urljoin, urlparse


class FieldSpec(BaseModel):
    xpath: str = Field(alias="@xpath")


class ExtractStep(BaseModel):
    xpath: str = Field(alias="@xpath")
    name: str = Field(default=None, alias="@name")
    fields: Dict[str, str] = Field(alias="@fields")  # Field name -> XPath
    follow: Optional["FollowStep"] = Field(default=None, alias="@follow")


class FollowStep(BaseModel):
    xpath: str = Field(alias="@xpath")
    steps: List['Step'] = Field(alias="@steps")  # Now supports recursive steps!
    max_depth: Optional[int] = Field(default=3, alias="@max-depth")
    detect_cycles: bool = Field(default=True, alias="@detect-cycles")
    follow_external: bool = Field(default=False, alias="@follow-external")


class PaginationSpec(BaseModel):
    xpath: str = Field(alias="@xpath")
    limit: int = Field(alias="@limit")


# New Action System Models
class ClickAction(BaseModel):
    type: Literal["click"] = Field(alias="@type")
    selector: str = Field(alias="@selector")
    xpath: Optional[str] = Field(default=None, alias="@xpath")  # Alternative to selector


class ScrollAction(BaseModel):
    type: Literal["scroll"] = Field(alias="@type")
    direction: Literal["up", "down", "left", "right"] = Field(default="down", alias="@direction")
    pixels: Optional[int] = Field(default=None, alias="@pixels")
    selector: Optional[str] = Field(default=None, alias="@selector")  # Scroll to element


class WaitAction(BaseModel):
    type: Literal["wait"] = Field(alias="@type")
    until: Literal["element", "text", "timeout", "network-idle"] = Field(alias="@until")
    selector: Optional[str] = Field(default=None, alias="@selector")  # For element/text waits
    xpath: Optional[str] = Field(default=None, alias="@xpath")  # Alternative to selector
    text: Optional[str] = Field(default=None, alias="@text")  # For text waits
    timeout: Optional[int] = Field(default=5000, alias="@timeout")  # Timeout in milliseconds


class FillAction(BaseModel):
    type: Literal["fill"] = Field(alias="@type")
    selector: str = Field(alias="@selector")
    xpath: Optional[str] = Field(default=None, alias="@xpath")
    value: str = Field(alias="@value")


class HoverAction(BaseModel):
    type: Literal["hover"] = Field(alias="@type")
    selector: str = Field(alias="@selector")
    xpath: Optional[str] = Field(default=None, alias="@xpath")


class JavaScriptAction(BaseModel):
    type: Literal["javascript"] = Field(alias="@type")
    code: str = Field(alias="@code")  # JavaScript code to execute
    wait_for: Optional[str] = Field(default=None, alias="@wait-for")  # JS condition to wait for
    timeout: Optional[int] = Field(default=5000, alias="@timeout")  # Timeout in milliseconds
    return_value: Optional[str] = Field(default=None, alias="@return-as")  # Variable name for return value


# Union type for all action types
Action = Union[ClickAction, ScrollAction, WaitAction, FillAction, HoverAction, JavaScriptAction]


# New Conditional System Models (v0.7+)
class ConditionSpec(BaseModel):
    """Defines a condition to evaluate"""
    exists: Optional[str] = Field(default=None, alias="@exists")  # Element exists check
    not_exists: Optional[str] = Field(default=None, alias="@not-exists")  # Element doesn't exist
    contains: Optional[str] = Field(default=None, alias="@contains")  # Text content check
    selector: Optional[str] = Field(default=None, alias="@selector")  # Element for text checks
    xpath: Optional[str] = Field(default=None, alias="@xpath")  # XPath alternative
    count: Optional[int] = Field(default=None, alias="@count")  # Element count check
    min_count: Optional[int] = Field(default=None, alias="@min-count")  # Minimum count
    max_count: Optional[int] = Field(default=None, alias="@max-count")  # Maximum count


class ConditionalStep(BaseModel):
    """A conditional execution step"""
    condition: ConditionSpec = Field(alias="@if")
    then_steps: List['Step'] = Field(alias="@then")  # Forward reference
    else_steps: Optional[List['Step']] = Field(default=None, alias="@else")  # Forward reference


class JavaScriptStep(BaseModel):
    """Execute JavaScript for data extraction"""
    code: str = Field(alias="@javascript")  # JavaScript code to execute
    name: Optional[str] = Field(default=None, alias="@name")  # Name for results
    timeout: Optional[int] = Field(default=5000, alias="@timeout")  # Timeout in milliseconds
    return_json: bool = Field(default=True, alias="@return-json")  # Whether to parse return as JSON


class JsonLdStep(BaseModel):
    """Extract JSON-LD structured data"""
    schema_type: Optional[str] = Field(default=None, alias="@schema")  # Filter by schema.org type
    fields: Optional[List[str]] = Field(default=None, alias="@fields")  # Specific fields to extract
    name: Optional[str] = Field(default=None, alias="@name")  # Name for results
    all_schemas: bool = Field(default=False, alias="@all-schemas")  # Extract all JSON-LD data


class ApiStep(BaseModel):
    """Extract data from API endpoints discovered on the page"""
    endpoint_pattern: Optional[str] = Field(default=None, alias="@endpoint")  # API endpoint pattern to match
    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(default="GET", alias="@method")  # HTTP method
    headers: Optional[Dict[str, str]] = Field(default=None, alias="@headers")  # Custom headers
    params: Optional[Dict[str, Union[str, int]]] = Field(default=None, alias="@params")  # Query parameters
    body: Optional[Dict[str, Any]] = Field(default=None, alias="@body")  # Request body for POST/PUT
    response_type: Literal["json", "text", "xml"] = Field(default="json", alias="@response-type")  # Expected response type
    json_path: Optional[str] = Field(default=None, alias="@json-path")  # JSONPath to extract specific data
    fields: Optional[List[str]] = Field(default=None, alias="@fields")  # Specific fields to extract from JSON
    name: Optional[str] = Field(default=None, alias="@name")  # Name for results
    timeout: Optional[int] = Field(default=10000, alias="@timeout")  # Request timeout in milliseconds
    follow_pagination: bool = Field(default=False, alias="@follow-pagination")  # Auto-follow pagination links
    max_pages: Optional[int] = Field(default=10, alias="@max-pages")  # Maximum pages to follow


class AiSelectStep(BaseModel):
    """AI-powered element selection using natural language"""
    find: str = Field(alias="@ai-select")  # Natural language description
    name: Optional[str] = Field(default=None, alias="@name")  # Name for results
    max_results: Optional[int] = Field(default=10, alias="@max-results")  # Maximum number of results


# Forward reference for recursive step definitions
Step = Union[ExtractStep, ConditionalStep, JavaScriptStep, JsonLdStep, ApiStep, AiSelectStep]


class ExtractionQuery(BaseModel):
    url: str = Field(alias="@url")
    steps: List[Step] = Field(alias="@steps")  # Updated to support conditionals
    actions: Optional[List[Action]] = Field(default=None, alias="@actions")  # New actions field
    pagination: Optional[PaginationSpec] = Field(default=None, alias="@pagination")

    # Updated configuration for Pydantic V2
    model_config = ConfigDict(populate_by_name=True)


# Fix forward references for recursive models (updated for Pydantic V2)
ExtractStep.model_rebuild()
FollowStep.model_rebuild()
ConditionalStep.model_rebuild()  # New conditional model
