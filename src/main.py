from celery.result import AsyncResult
from fastapi import FastAPI, Request, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from models.database import get_db
from services import uploads_file, task_status, get_result_def, delete_file_by_id

app = FastAPI()
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


@app.get("/result/{file_id}")
async def get_result(file_id: str, db: Session = Depends(get_db)):
    try:
        return await get_result_def(db, file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/file/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    try:
        return await delete_file_by_id(db, file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
