from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import models
from models.database import get_db
from schemas.collection import CollectionOut, CollectionDocumentsOut, CollectionStatisticsOut
from services.collection import calculate_collection_statistics
from services.user import UserService
from repositories.collection import CollectionRepository
from repositories.processed_file import ProcessedFileRepository

router = APIRouter(
    prefix="/collections",
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=List[CollectionOut], summary="Получить список коллекций")
async def get_collections(db: Session = Depends(get_db),
                          current_user: models.User = Depends(UserService.get_current_user)):
    try:
        collection_repo = CollectionRepository(db)
        collections = collection_repo.get_by_owner_id(current_user.id)

        result = []
        for collection in collections:
            documents = [{
                "file_id": pf.file_id,
                "filename": pf.filename,
                "file_path": pf.file_path
            } for pf in collection.processed_files]

            result.append(CollectionOut(
                collection_id=collection.id,
                documents=documents
            ))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{collection_id}", response_model=CollectionDocumentsOut, summary="Получить список документов в коллекции")
async def get_collection_documents(collection_id: int, db: Session = Depends(get_db)):
    try:
        collection_repo = CollectionRepository(db)
        documents = collection_repo.get_documents_in_collection(collection_id)

        if documents is None:
            raise HTTPException(status_code=404, detail="Collection not found")

        return CollectionDocumentsOut(
            collection_id=collection_id,
            documents=documents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{collection_id}/statistics", response_model=CollectionStatisticsOut,
            summary="Получить статистику по коллекции")
async def get_collection_statistics(collection_id: int, db: Session = Depends(get_db)):
    try:
        collection_repo = CollectionRepository(db)
        collection = collection_repo.get(collection_id)

        if collection is None:
            raise HTTPException(status_code=404, detail="Collection not found")

        statistics = calculate_collection_statistics(collection_id, db)

        return CollectionStatisticsOut(
            collection_id=collection_id,
            statistics=statistics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{collection_id}/{document_id}", summary="Добавить документ в коллекцию")
async def add_document_to_collection(collection_id: int, document_id: int, db: Session = Depends(get_db)):
    try:
        collection_repo = CollectionRepository(db)
        processed_file_repo = ProcessedFileRepository(db)

        # Проверяем, существует ли коллекция
        collection = collection_repo.get(collection_id)
        if collection is None:
            raise HTTPException(status_code=404, detail="Collection not found")

        # Получаем документ по его id
        document = processed_file_repo.get(document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        # Обновляем коллекцию документа
        processed_file_repo.update(document, {"collection_id": collection_id})

        return {"message": "Document added to collection successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{collection_id}/{document_id}", summary="Удалить документ из коллекции")
async def remove_document_from_collection(collection_id: int, document_id: int, db: Session = Depends(get_db)):
    try:
        processed_file_repo = ProcessedFileRepository(db)

        # Получаем документ по его id
        document = processed_file_repo.get(document_id)

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        # Проверяем, что документ действительно принадлежит указанной коллекции
        if document.collection_id != collection_id:
            raise HTTPException(status_code=404, detail="Document does not belong to the specified collection")

        # Удаляем связь с коллекцией
        processed_file_repo.update(document, {"collection_id": None})

        return {"message": "Document removed from collection successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
