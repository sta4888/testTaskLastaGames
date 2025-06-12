from sqlalchemy.orm import Session
from models.models import WordStat
from repositories.base import BaseRepository


class WordStatRepository(BaseRepository[WordStat]):
    def __init__(self, db: Session):
        super().__init__(WordStat, db)

    def get_by_term(self, term: str):
        return self.db.query(self.model).filter(self.model.term == term).all()

    def get_by_file_id(self, file_id: str):
        return self.db.query(self.model).filter(self.model.file_id == file_id).all()

    def count_by_file_id(self, file_id: str) -> int:
        return self.db.query(self.model).filter(self.model.file_id == file_id).count()

    def get_by_file_id_paginated(self, file_id: str, offset: int, limit: int):
        return (
            self.db.query(self.model)
            .filter(self.model.file_id == file_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

