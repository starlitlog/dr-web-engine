from pydantic import BaseModel, Field
from typing import Dict, List, Optional


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


class ExtractionQuery(BaseModel):
    url: str = Field(alias="@url")
    steps: List[ExtractStep] = Field(alias="@steps")
    pagination: Optional[PaginationSpec] = Field(default=None, alias="@pagination")

    class Config:
        allow_population_by_field_name = True


# Fix forward references for recursive models
ExtractStep.update_forward_refs()
FollowStep.update_forward_refs()
