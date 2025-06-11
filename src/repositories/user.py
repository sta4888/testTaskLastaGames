from sqlalchemy.orm import Session
from models.models import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str):
        return self.db.query(self.model).filter(self.model.username == username).first()

    def get_by_email(self, email: str):
        return self.db.query(self.model).filter(self.model.email == email).first()

    def create(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User):
        self.db.delete(user)