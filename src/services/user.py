from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_db
from repositories.user import UserRepository
from utils.auth import verify_password, create_access_token, get_password_hash, oauth2_scheme, decode_token
from typing import Optional
from datetime import timedelta
from settings import settings
from models.models import User


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def generate_token_for_user(self, user: User) -> str:
        token_data = {"sub": str(user.id)}
        return create_access_token(token_data, timedelta(minutes=settings.access_token_expire_minutes))

    def get_user_by_token(self, token: str) -> Optional[User]:
        from utils.auth import decode_token
        user_id = decode_token(token)
        if user_id is None:
            return None
        return self.repo.get(int(user_id))

    def create_user(self, username: str, password: str) -> User:
        hashed_pw = get_password_hash(password)
        user = self.repo.create(username=username, hashed_password=hashed_pw)
        return user

    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

