from sqlalchemy.orm import Session
from models.models import ProcessedFile
from repositories.base import BaseRepository


class ProcessedFileRepository(BaseRepository[ProcessedFile]):
    def __init__(self, db: Session):
        super().__init__(ProcessedFile, db)

    def get_by_file_hash(self, file_hash: str):
        return self.db.query(self.model).filter(self.model.file_hash == file_hash).first()

    def get_by_owner_id(self, owner_id: int):
        return self.db.query(self.model).filter(self.model.owner_id == owner_id).all()
