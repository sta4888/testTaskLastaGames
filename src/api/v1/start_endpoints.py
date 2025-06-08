from fastapi import APIRouter
from celery.result import AsyncResult
from fastapi import UploadFile, HTTPException, Depends, Query

from sqlalchemy.orm import Session
from models.database import get_db
from schemas import ProcessedResultResponse
from services import uploads_file, task_status, get_result_def, delete_file_by_id

router = APIRouter()


@router.post("/upload/")
async def upload_file(file: UploadFile):
    try:
        return await uploads_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    return await task_status(task)


@router.get("/result/{file_id}", response_model=ProcessedResultResponse)
async def get_result(
        file_id: str,
        page: int = Query(1, ge=1),
        page_size: int = Query(50, le=100),
        db: Session = Depends(get_db)
):
    try:
        # Передаем параметры пагинации в функцию получения данных
        return await get_result_def(db, file_id, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    try:
        return await delete_file_by_id(db, file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
