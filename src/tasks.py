from dfidf import Df_Idf
from models.models import Collection
from repositories.processed_file import ProcessedFileRepository
from models.database import SessionLocal

from worker import app
import time

@app.task
def process_file_task(
    file_path: str,
    file_id: str,
    file_hash: str,
    filename: str,
    owner_id: int
) -> dict:
    start_time = time.time()
    db = SessionLocal()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        result = {
            "lines_count": len(lines),
            "first_line": lines[0].strip() if lines else None,
            "last_line": lines[-1].strip() if lines else None,
            "processing_status": "completed"
        }

        # Создаём запись через репозиторий
        processed_file_repo = ProcessedFileRepository(db)
        processed_file = processed_file_repo.create(
            file_id=file_id,
            result=result,
            file_path=file_path,
            status="completed",
            filename=filename,
            file_hash=file_hash,
            owner_id=owner_id
        )

        # Обработка TF-IDF и сохранение
        df_idf = Df_Idf(file_path=file_path, file_id=file_id, db=db)
        df_idf.save_to_db(processed_file.id)

        # Определяем коллекцию для файла
        collection_id = df_idf.group_documents_by_common_words()

        # Проверяем, существует ли коллекция, и если нет, создаем её
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            collection = Collection(owner_id=owner_id)
            db.add(collection)
            db.commit()
            db.refresh(collection)
            collection_id = collection.id

        processed_file.collection_id = collection_id

        # Обновляем время обработки
        time_elapsed = round(time.time() - start_time, 3)
        processed_file_repo.update(processed_file, {"time_processed": time_elapsed, "collection_id": collection_id})

        db.close()
        return result

    except Exception as e:
        time_elapsed = round(time.time() - start_time, 3)
        # В случае ошибки — тоже через репозиторий
        processed_file_repo = ProcessedFileRepository(db)
        processed_file_repo.create(
            file_id=file_id,
            error=str(e),
            file_path=file_path,
            status="failed",
            time_processed=time_elapsed
        )
        db.close()
        return {"error": str(e), "status": "failed"}
