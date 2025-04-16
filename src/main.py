import uuid

from celery.result import AsyncResult
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
import os

from database import get_db
from models import ProcessedFile
from tasks import process_file_task

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload_file(file: UploadFile):
    try:
        # Генерируем уникальный ID для файла
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            while content := await file.read(1024 * 1024):
                buffer.write(content)

        # Отправляем задачу в Celery
        task = process_file_task.delay(file_path, file_id)

        return {
            "file_id": file_id,
            "task_id": task.id,
            "status": "processing"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        return {"status": "processing"}
    elif task.state == 'SUCCESS':
        result = task.result
        return {"status": "completed", "result": result}
    elif task.state == 'FAILURE':
        return {"status": "failed", "error": str(task.info)}
    else:
        return {"status": task.state}


@app.get("/result/{file_id}")
async def get_result(file_id: str, db: Session = Depends(get_db)):
    try:
        processed_file = db.query(ProcessedFile).filter(ProcessedFile.file_id == file_id).first()
        if not processed_file:
            raise HTTPException(status_code=404, detail="File not found")

        return {
            "status": processed_file.status,
            "result": processed_file.result,
            "error": processed_file.error,
            "created_at": processed_file.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/file/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    try:
        # Удаляем запись из базы данных
        file = db.query(ProcessedFile).filter(ProcessedFile.file_id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Удаляем файл с диска
        file_path = os.path.join("uploaded_files", f"{file_id}_{file.file_id}")
        if os.path.exists(file_path):
            os.remove(file_path)

        # Удаляем запись из базы
        db.delete(file)
        db.commit()

        return {"status": "success", "message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
