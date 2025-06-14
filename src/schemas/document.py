from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentListItem(BaseModel):
    id: int
    name: str


class DocumentResult(BaseModel):
    lines_count: Optional[int]
    text: str




class MessageResponse(BaseModel):
    message: str