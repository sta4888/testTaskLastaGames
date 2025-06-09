from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import User
from schemas.user import UserCreate
from services.user import authenticate_user, create_access_token, verify_password, get_password_hash

router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}}
)


@router.post("/login", summary="авторизация по логину и паролю")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", summary="создание пользователя по логину и паролю")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created"}


@router.get("/logout", summary="завершение сессии пользователя")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


@router.patch("/{user_id}", summary="изменение пароля, переданного в теле запроса")
async def edit_user(user_id: int, old_password: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Password changed"}


@router.delete("/{user_id}", summary="удаление пользователя")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
