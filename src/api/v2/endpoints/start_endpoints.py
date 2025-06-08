from fastapi import APIRouter

from settings import settings

router = APIRouter()


@router.get("/status", summary="Получить статуса приложения")
async def get_app_status():
    return {"status": "OK"}


@router.get("/version", summary="Получить версию приложения")
async def get_app_version():
    return {"version": settings.project.release_version}