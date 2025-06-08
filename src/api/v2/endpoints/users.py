from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}}
)


@router.post("/login", summary="авторизация по логину и паролю")
async def login_user(request: Request):
    return {"status": "OK"}


@router.post("/register", summary="создание пользователя по логину и паролю")
async def register_user(request: Request):
    return {"status": "OK"}


@router.get("/logout", summary="завершение сессии пользователя")
async def get_app_status():
    return {"status": "OK"}


@router.patch("/{user_id}", summary="изменение пароля, переданного в теле запроса")
async def edit_user(request: Request, user_id: int):
    return {"status": "OK"}


@router.delete("/{user_id}", summary="удаление пользователя")
async def delete_user(request: Request, user_id: int):
    return {"status": "OK"}
