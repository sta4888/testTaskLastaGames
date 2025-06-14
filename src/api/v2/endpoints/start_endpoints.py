from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db
from repositories.processed_file import ProcessedFileRepository
from services.services import get_custom_metrics
from settings import settings

router = APIRouter()


@router.get("/status", summary="Получить статуса приложения")
async def get_app_status():
    return {"status": "OK"}


@router.get("/version", summary="Получить версию приложения")
async def get_app_version():
    return {"version": settings.project.release_version}

@router.get("/metrics", summary="Получить метрики обработки файлов")
async def get_app_metrics(db: Session = Depends(get_db)):
    return await get_custom_metrics(db)