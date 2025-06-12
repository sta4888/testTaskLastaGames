from pydantic import BaseModel
from typing import List, Dict

class DocumentOut(BaseModel):
    file_id: str
    filename: str
    file_path: str

class CollectionOut(BaseModel):
    collection_id: int
    documents: List[DocumentOut]

class CollectionDocumentsOut(BaseModel):
    collection_id: int
    documents: List[str]

class CollectionStatisticsOut(BaseModel):
    collection_id: int
    statistics: Dict
