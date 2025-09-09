from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Union, Literal


class FieldSpec(BaseModel):
    xpath: str = Field(alias="@xpath")


class ExtractStep(BaseModel):
    xpath: str = Field(alias="@xpath")
    name: str = Field(default=None, alias="@name")
    fields: Dict[str, str] = Field(alias="@fields")  # Field name -> XPath
    follow: Optional["FollowStep"] = Field(default=None, alias="@follow")


class FollowStep(BaseModel):
    xpath: str = Field(alias="@xpath")
    steps: List[ExtractStep] = Field(alias="@steps")


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


# Union type for all action types
Action = Union[ClickAction, ScrollAction, WaitAction, FillAction, HoverAction]


class ExtractionQuery(BaseModel):
    url: str = Field(alias="@url")
    steps: List[ExtractStep] = Field(alias="@steps")
    actions: Optional[List[Action]] = Field(default=None, alias="@actions")  # New actions field
    pagination: Optional[PaginationSpec] = Field(default=None, alias="@pagination")

    # Updated configuration for Pydantic V2
    model_config = ConfigDict(populate_by_name=True)


# Fix forward references for recursive models (updated for Pydantic V2)
ExtractStep.model_rebuild()
FollowStep.model_rebuild()
