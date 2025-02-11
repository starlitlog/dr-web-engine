from pydantic import BaseModel, Field, ConfigDict
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

    # Updated configuration for Pydantic V2
    model_config = ConfigDict(populate_by_name=True)


# Fix forward references for recursive models (updated for Pydantic V2)
ExtractStep.model_rebuild()
FollowStep.model_rebuild()
