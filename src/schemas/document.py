from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    content: str

class DocumentOut(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True

class DocumentDetail(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True

class DocumentStats(BaseModel):
    word_count: int
    char_count: int

class DocumentListItem(BaseModel):
    id: int
    filename: str

    class Config:
        orm_mode = True