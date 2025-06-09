import hashlib
import os
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.models import ProcessedFile, WordStat, Document
from schemas.schemas import ProcessedResultResponse, TermResponse
from tasks import process_file_task

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def uploads_file(file, user_id: int, db: Session):
    """
    Функция загрузки и обработки файла
    :param file:
    :return:
    """
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Сохраняем файл
    hash_md5 = hashlib.md5()
    with open(file_path, "wb") as buffer:
        while content := await file.read(1024 * 1024):
            buffer.write(content)
            hash_md5.update(content)

    file_hash = hash_md5.hexdigest()

    # Сохраняем в БД как Document
    document = Document(
        filename=file.filename,
        filepath=file_path,
        file_hash=file_hash,
        owner_id=user_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Запускаем Celery-задачу
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


async def get_result_def(db, file_id: str, page: int = 1, page_size: int = 50):
    """
    Функция возврата результата обработки файла с дополнительными данными из WordStat
    :param db:
    :param file_id:
    :return:
    """

    processed_file = db.query(ProcessedFile).filter(ProcessedFile.file_id == file_id).first()
    if not processed_file:
        raise HTTPException(status_code=404, detail="File not found")

    total_terms = db.query(WordStat).filter(WordStat.file_id == file_id).count()
    total_pages = (total_terms + page_size - 1) // page_size

    if page > total_pages or page < 1:
        raise HTTPException(status_code=400, detail="Page out of range")

    word_stats = db.query(WordStat).filter(WordStat.file_id == file_id).offset((page - 1) * page_size).limit(
        page_size).all()

    if not word_stats:
        raise HTTPException(status_code=404, detail="WordStats not found")

    terms = [
        TermResponse(word=word_stat.term, tf=word_stat.tf, idf=word_stat.idf)
        for word_stat in word_stats
    ]

    return ProcessedResultResponse(
        status=processed_file.status,
        result=processed_file.result,
        error=processed_file.error,
        created_at=processed_file.created_at,
        terms=terms,
        total_terms=total_terms,
        page=page,
        total_pages=total_pages
    )


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
