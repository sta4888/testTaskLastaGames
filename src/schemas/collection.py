from typing import List

from pydantic import BaseModel


class CollectionBase(BaseModel):
    id: int
    documents: List[int] = []


class CollectionStatistics(BaseModel):
    tf: dict[str, int]
    idf: dict[str, float]