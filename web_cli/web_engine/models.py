from pydantic import BaseModel
from typing import Dict, List, Optional


class FieldSpec(BaseModel):
    xpath: str


class ExtractStep(BaseModel):
    xpath: str
    fields: Dict[str, str]  # Field name -> XPath
    follow: Optional["FollowStep"] = None


class FollowStep(BaseModel):
    xpath: str
    steps: List[ExtractStep]


class PaginationSpec(BaseModel):
    xpath: str
    limit: int


class ExtractionQuery(BaseModel):
    url: str
    steps: List[ExtractStep]
    pagination: Optional[PaginationSpec] = None

