from dfidf import Df_Idf
from models.database import SessionLocal
from models.models import ProcessedFile
from worker import app


@app.task
def process_file_task(file_path: str, file_id: str) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        result = {
            "lines_count": len(lines),
            "first_line": lines[0].strip() if lines else None,
            "last_line": lines[-1].strip() if lines else None,
            "processing_status": "completed"
        }

        db = SessionLocal()
        processed_file = ProcessedFile(
            file_id=file_id,
            result=result,
            file_path=file_path,
            status="completed"
        )
        db.add(processed_file)
        db.commit()
        db.refresh(processed_file)

        df_idf = Df_Idf(file_path=file_path, file_id=file_id, db=db)

        df_idf.save_to_db(processed_file.id)

        db.close()

        return result

    except Exception as e:
        db = SessionLocal()
        processed_file = ProcessedFile(
            file_id=file_id,
            error=str(e),
            file_path=file_path,
            status="failed"
        )
        db.add(processed_file)
        db.commit()
        db.close()
        return {"error": str(e), "status": "failed"}