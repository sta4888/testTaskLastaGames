from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TermResponse(BaseModel):
    word: str
    tf: int
    idf: float


class ProcessedResultResponse(BaseModel):
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime
    terms: List[TermResponse]
    total_terms: int
    page: int
    total_pages: int
