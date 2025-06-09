import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import Document
from schemas.document import DocumentListItem
from services.document import get_current_user

router = APIRouter(
    prefix="/documents",
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=List[DocumentListItem], summary="получить список документов")
async def get_documents(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    documents = db.query(Document).filter(Document.owner_id == current_user.id).all()
    return documents


@router.get("/{document_id}", summary="получить содержимое документа")
async def get_document(
        document_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(path=document.filepath, filename=document.filename, media_type="application/octet-stream")


@router.get("/{document_id}/statistics", summary="получить статистику по документу")
async def get_document_statistics(
        document_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_stats = document.statistics
    if not doc_stats:
        raise HTTPException(status_code=404, detail="Document statistics not found")

    # Собираем статистику документа + коллекций
    collection_stats = []
    for rel in document.collections:
        collection = rel.collection
        if collection.statistics:
            collection_stats.append({
                "collection_id": collection.id,
                "collection_name": collection.name,
                "tf_idf_data": collection.statistics.tf_idf_data,
            })

    return {
        "document_id": document.id,
        "filename": document.filename,
        "tf_idf_data": doc_stats.tf_idf_data,
        "collections": collection_stats
    }


@router.delete("/{document_id}", summary="удалить документ")
async def delete_document(
        document_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Удаление физического файла
        if os.path.exists(document.filepath):
            os.remove(document.filepath)

        db.delete(document)
        db.commit()
        return {"detail": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
