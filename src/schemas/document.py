from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentListItem(BaseModel):
    id: int
    name: str


class DocumentResult(BaseModel):
    lines_count: Optional[int]
    first_line: Optional[str]
    last_line: Optional[str]
    processing_status: Optional[str]




class MessageResponse(BaseModel):
    message: str