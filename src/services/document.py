from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import User
from utils.auth import decode_token, oauth2_scheme



