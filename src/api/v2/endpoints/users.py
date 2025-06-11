from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.database import get_db
from schemas.user import UserCreate
from services.user import UserService
from utils.auth import get_password_hash, verify_password

router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}}
)


@router.post("/login", summary="Авторизация по логину и паролю")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")

    token = service.generate_token_for_user(user)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", summary="Создание нового пользователя")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)

    if service.repo.get_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    service.create_user(username=user_data.username, password=user_data.password)
    return {"message": "Пользователь успешно создан"}


@router.get("/logout", summary="Завершение сессии пользователя")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Вы вышли из системы"}


@router.patch("/{user_id}", summary="Изменение пароля")
async def change_password(user_id: int, old_password: str, new_password: str, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.repo.get(user_id)

    if not user or not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверные учетные данные")

    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Пароль успешно изменён"}


@router.delete("/{user_id}", summary="Удаление пользователя")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    service.repo.delete(user)
    db.commit()
    return {"message": "Пользователь удалён"}
