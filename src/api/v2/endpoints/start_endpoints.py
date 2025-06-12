from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db
from repositories.processed_file import ProcessedFileRepository
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
    processed_file_repo = ProcessedFileRepository(db)

    # Получаем все обработанные файлы
    processed_files = processed_file_repo.get_all()

    if not processed_files:
        return {
            "files_processed": 0,
            "min_time_processed": 0.0,
            "avg_time_processed": 0.0,
            "max_time_processed": 0.0,
            "latest_file_processed_timestamp": None
        }

    # Рассчитываем количество обработанных файлов
    files_processed = len(processed_files)

    # Рассчитываем минимальное, среднее и максимальное время обработки
    times_processed = [float(file.time_processed) for file in processed_files]
    min_time_processed = min(times_processed)
    avg_time_processed = sum(times_processed) / len(times_processed)
    max_time_processed = max(times_processed)

    # Определяем время обработки последнего файла
    latest_file_processed_timestamp = max(file.created_at for file in processed_files).timestamp()

    return {
        "files_processed": files_processed,
        "min_time_processed": round(min_time_processed, 3),
        "avg_time_processed": round(avg_time_processed, 3),
        "max_time_processed": round(max_time_processed, 3),
        "latest_file_processed_timestamp": latest_file_processed_timestamp
    }