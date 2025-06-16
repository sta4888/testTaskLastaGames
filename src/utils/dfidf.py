import math
import re
from collections import Counter, defaultdict

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.models import WordStat

class Df_Idf:
    def __init__(self, file_path, file_id, db):
        self.file_path = file_path
        self.file_id = file_id
        self.db = db
        self.documents = self._load_documents()
        self.tokenized_docs = [self._tokenize(doc) for doc in self.documents]
        self.flat_terms = [term for doc in self.tokenized_docs for term in doc]
        self.tf_counter = Counter(self.flat_terms)
        self.df_counter = self._compute_df()
        self.idf = self._compute_idf()

    def _load_documents(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при чтении файла: {str(e)}")

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def _compute_df(self):
        df = defaultdict(int)
        for doc in self.tokenized_docs:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] += 1
        return df

    def _compute_idf(self):
        N = len(self.tokenized_docs)
        return {term: math.log(N / (1 + df)) for term, df in self.df_counter.items()}

    def save_to_db(self, processed_file_id):
        try:
            for term in self.tf_counter:
                word_stat = WordStat(
                    file_id=self.file_id,
                    term=term,
                    tf=self.tf_counter[term],
                    idf=round(self.idf.get(term, 0), 6),
                    processed_file_id=processed_file_id,
                )
                self.db.add(word_stat)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при сохранении в базу данных: {str(e)}")

    def get_paginated_result(self, page: int = 1, page_size: int = 50):
        all_terms = [
            {
                "term": term,
                "tf": self.tf_counter[term],
                "idf": round(self.idf.get(term, 0), 6)
            }
            for term in self.tf_counter
        ]

        sorted_terms = sorted(all_terms, key=lambda x: x["idf"], reverse=True)

        start = (page - 1) * page_size
        end = start + page_size
        paginated = sorted_terms[start:end]

        return {
            "total_terms": len(sorted_terms),
            "page": page,
            "page_size": page_size,
            "data": paginated
        }

    def group_documents_by_common_words(self, min_collections=3):
        """
        Разбивает документы на коллекции по общим словам.
        Возвращает id коллекции, к которой можно добавить новый документ.
        """
        # Извлекаем данные из базы данных для всех предыдущих документов
        previous_docs_stats = self._load_previous_documents_stats()

        # Создаем множества слов для каждого документа
        current_doc_set = set(self._tokenize(self.documents[0]))
        previous_doc_sets = [set(self._tokenize(doc['document'])) for doc in previous_docs_stats]

        # Ищем пересечения с предыдущими документами
        collection_id = None
        for doc_id, doc_set in enumerate(previous_doc_sets):
            if current_doc_set & doc_set:  # если есть пересечение
                collection_id = doc_id
                break

        # Если не нашли пересечений, создаем новую коллекцию
        if collection_id is None:
            collection_id = len(previous_doc_sets)

        return collection_id

    def _load_previous_documents_stats(self):
        """
        Извлекает статистику предыдущих документов из базы данных.
        """
        try:
            # Предположим, что у вас есть метод для извлечения данных из базы данных
            previous_docs = self.db.query(WordStat).filter(WordStat.file_id != self.file_id).all()

            # Группируем данные по документам
            docs_stats = defaultdict(list)
            for doc in previous_docs:
                docs_stats[doc.file_id].append({
                    'term': doc.term,
                    'tf': doc.tf,
                    'idf': doc.idf
                })

            # Преобразуем данные в удобный формат
            documents = []
            for file_id, stats in docs_stats.items():
                document = ' '.join([term['term'] for term in stats])
                documents.append({'file_id': file_id, 'document': document})

            return documents
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при загрузке данных из базы данных: {str(e)}")
