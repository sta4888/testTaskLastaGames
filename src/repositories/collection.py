from sqlalchemy.orm import Session
from models.models import Collection
from repositories.base import BaseRepository

class CollectionRepository(BaseRepository[Collection]):
    def __init__(self, db: Session):
        super().__init__(Collection, db)

    def get_by_owner_id(self, owner_id: int):
        return self.db.query(self.model).filter(self.model.owner_id == owner_id).all()

    def get_documents_in_collection(self, collection_id: int):
        collection = self.get(collection_id)
        if collection:
            return [pf.file_id for pf in collection.processed_files]
        return []
