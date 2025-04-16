import os
import uuid

from fastapi import HTTPException

from models.models import ProcessedFile
from tasks import process_file_task

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def uploads_file(file):
    """
    Функция загрузки и обработки файла
    :param file:
    :return:
    """
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        while content := await file.read(1024 * 1024):
            buffer.write(content)

    task = process_file_task.delay(file_path, file_id)

    return {
        "file_id": file_id,
        "task_id": task.id,
        "status": "processing"
    }


async def task_status(task):
    """
    Функция проверки статуса задачи
    :param task:
    :return:
    """
    if task.state == 'PENDING':
        return {"status": "processing"}
    elif task.state == 'SUCCESS':
        result = task.result
        return {"status": "completed", "result": result}
    elif task.state == 'FAILURE':
        return {"status": "failed", "error": str(task.info)}
    else:
        return {"status": task.state}


async def get_result_def(db, file_id):
    """
    Функция возврата результата обработки файла
    :param db:
    :param file_id:
    :return:
    """
    processed_file = db.query(ProcessedFile).filter(ProcessedFile.file_id == file_id).first()
    if not processed_file:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "status": processed_file.status,
        "result": processed_file.result,
        "error": processed_file.error,
        "created_at": processed_file.created_at
    }

async def delete_file_by_id(db, file_id):
    """
    Функция удаления файла и его данных
    :param db:
    :param file_id:
    :return:
    """
    file = db.query(ProcessedFile).filter(ProcessedFile.file_id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.file_id}")
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(file)
    db.commit()

    return {"status": "success", "message": "File deleted successfully"}


