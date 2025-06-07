from celery.result import AsyncResult
from fastapi import FastAPI, Request, UploadFile, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from models.database import get_db
from schemas import ProcessedResultResponse
from serialize import serialize_datetime
from services import uploads_file, task_status, get_result_def, delete_file_by_id
from settings import settings

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)
Instrumentator().instrument(app).expose(app)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload_file(file: UploadFile):
    try:
        return await uploads_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    return await task_status(task)


@app.get("/status", summary="Получить статуса приложения", response_model=dict)
async def get_app_status():
    return {"status": "OK"}


@app.get("/version", summary="Получить версию приложения", response_model=dict)
async def get_app_version():
    return {"version": settings.project.release_version}


@app.get("/result/{file_id}", response_model=ProcessedResultResponse)
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


@app.delete("/file/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    try:
        return await delete_file_by_id(db, file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
