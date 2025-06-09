import math
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import Collection, Document

router = APIRouter(
    prefix="/collection",
    responses={404: {"description": "Not found"}}
)


@router.get("/", summary="получить список коллекций")
async def get_collections(db: Session = Depends(get_db)):
    collections = db.query(Collection).all()
    return [
        {
            "id": c.id,
            "documents": [d.id for d in c.documents]
        }
        for c in collections
    ]


@router.get("/{collection_id}", summary="получить список документов коллекции")
async def get_collection(collection_id: int, db: Session = Depends(get_db)):
    collection = db.query(Collection).get(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return [doc.id for doc in collection.documents]


@router.get("/{collection_id}/statistics", summary="получить статистику по коллекции")
async def get_collection_statistics(collection_id: int, db: Session = Depends(get_db)):
    collection = db.query(Collection).get(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Объединяем все тексты коллекции
    all_text = " ".join(doc.content for doc in collection.documents)
    tokens = all_text.lower().split()
    tf = Counter(tokens)

    # IDF (по всем документам в БД)
    total_docs = db.query(Document).count()
    idf = {}
    for word in tf:
        doc_count = db.query(Document).filter(Document.content.ilike(f"%{word}%")).count()
        idf[word] = math.log(total_docs / (1 + doc_count))  # сглаживание

    return {
        "tf": dict(tf),
        "idf": idf
    }


@router.post("/{collection_id}/{document_id}", summary="добавить документ в коллекцию")
async def add_document_to_collection(collection_id: int, document_id: int, db: Session = Depends(get_db)):
    collection = db.query(Collection).get(collection_id)
    document = db.query(Document).get(document_id)

    if not collection or not document:
        raise HTTPException(status_code=404, detail="Collection or document not found")

    if document not in collection.documents:
        collection.documents.append(document)
        db.commit()

    return {"message": "Document added to collection"}


@router.delete("/{collection_id}/{document_id}", summary="удалить документ из коллекции")
async def delete_document_from_collection(collection_id: int, document_id: int, db: Session = Depends(get_db)):
    collection = db.query(Collection).get(collection_id)
    document = db.query(Document).get(document_id)

    if not collection or not document:
        raise HTTPException(status_code=404, detail="Collection or document not found")

    if document in collection.documents:
        collection.documents.remove(document)
        db.commit()

    return {"message": "Document removed from collection"}
