import os
import uuid

from fastapi import HTTPException

from models.models import ProcessedFile
from tasks import process_file_task
import math

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

#
# class Df_Idf:
#     # нужно получить документ
#     # считать его
#     # взять все слова
#     # вычислить уникальность
#
#     def __init__(self, doc_id, db):
#         self.doc_id = doc_id
#         self.db = db
#
#
#     def _get_doc_by_id(self):
#         file = self.db.query(ProcessedFile).filter(ProcessedFile.file_id == self.doc_id).first()
#         if not file:
#             raise HTTPException(status_code=404, detail="File not found")
#         return file
#
#     def _load_documents(self):
#         file = self._get_doc_by_id()
#         try:
#             with open(file.path, 'r', encoding='utf-8') as f:
#                 return [line.strip() for line in f.readlines() if line.strip()]
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Ошибка при чтении файла: {str(e)}")
#
#
#     # def _compute_tf(self, doc):
#     #     tf = {}
#     #     total_words = len(doc)
#     #     for word in doc:
#     #         tf[word] = tf.get(word, 0) + 1
#     #     for word in tf:
#     #         tf[word] /= total_words
#     #     return tf
#     #
#     # def _compute_idf(self):
#     #     N = len(self.tokenized_docs)
#     #     idf = {}
#     #     for word in self.all_words:
#     #         containing_docs = sum(1 for doc in self.tokenized_docs if word in doc)
#     #         idf[word] = math.log(N / (1 + containing_docs), 10)
#     #     return idf
#     #
#     # def _compute_tfidf(self, tf):
#     #     return {word: tf[word] * self.idf[word] for word in tf}
#
#     def get_result(self):
#         print(self._load_documents())
#         # return {
#         #     "doc_id": self.doc_id,
#         #     "documents_count": len(self.documents),
#         #     "tfidf": self.tfidf_list
#         # }
#
#     # # Пример документов
#     # documents = [
#     #     "кошка любит молоко",
#     #     "собака любит мясо",
#     #     "кошка и собака друзья"
#     # ]
#     #
#     # # Шаг 1: Разделяем документы на слова
#     # tokenized_docs = [doc.lower().split() for doc in documents]
#     #
#     # # Список всех уникальных слов в корпусе
#     # all_words = sorted(set(word for doc in tokenized_docs for word in doc))
#     #
#     # # Шаг 2: TF (Term Frequency)
#     # def compute_tf(doc):
#     #     tf = {}
#     #     total_words = len(doc)
#     #     for word in doc:
#     #         tf[word] = tf.get(word, 0) + 1
#     #     for word in tf:
#     #         tf[word] /= total_words
#     #     return tf
#     #
#     # # Шаг 3: IDF (Inverse Document Frequency)
#     # def compute_idf(docs):
#     #     N = len(docs)
#     #     idf = {}
#     #     for word in all_words:
#     #         containing_docs = sum(1 for doc in docs if word in doc)
#     #         idf[word] = math.log((N / (1 + containing_docs)), 10)  # log base 10
#     #     return idf
#     #
#     # # Шаг 4: TF-IDF = TF * IDF
#     # def compute_tfidf(tf, idf):
#     #     return {word: tf[word] * idf[word] for word in tf}
#     #
#     # # Вычисляем TF для каждого документа
#     # tf_list = [compute_tf(doc) for doc in tokenized_docs]
#     #
#     # # Вычисляем IDF по всему корпусу
#     # idf = compute_idf(tokenized_docs)
#     #
#     # # Вычисляем TF-IDF
#     # tfidf_list = [compute_tfidf(tf, idf) for tf in tf_list]
#     #
#     # # Печатаем результат
#     # for i, tfidf in enumerate(tfidf_list):
#     #     print(f"\nДокумент {i + 1}: \"{documents[i]}\"")
#     #     for word in sorted(tfidf):
#     #         print(f"  {word}: {tfidf[word]:.4f}")
