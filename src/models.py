from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class RulebookState(str, Enum):
    ANSWERABLE = "ANSWERABLE"
    NOT_COVERED = "NOT_COVERED"
    CONTRADICTION = "CONTRADICTION"

class EvidenceItem(BaseModel):
    source: str = Field(description="Filename of the source document")
    section: str = Field(description="Section or chapter heading")
    page: Optional[int] = Field(default=None, description="Page number if PDF document")
    text: str = Field(description="Exact supporting passage text from the rulebook")

class QueryRequest(BaseModel):
    question: str = Field(description="User question in plain English")

class AnalysisResult(BaseModel):
    question: str
    state: RulebookState
    answer: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
