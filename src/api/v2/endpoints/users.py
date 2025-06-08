# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from models import User
# from schemas import UserCreate
# from crud.user import CRUDUser
#
# router = APIRouter()
# user_crud = CRUDUser(User)
#
# @router.post("/register")
# def register_user(user: UserCreate, db: Session = Depends(get_db)):
#     return user_crud.create(db, user.dict())