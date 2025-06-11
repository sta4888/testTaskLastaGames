from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import ProcessedFile
from repositories.processed_file import ProcessedFileRepository
from repositories.word_stat import WordStatRepository
from schemas.document import DocumentListItem, DocumentResult, MessageResponse
from schemas.schemas import TermResponse
from services.user import UserService

router = APIRouter(prefix="/documents")


@router.get("/", response_model=List[DocumentListItem], summary="получить список документов")
def get_documents(current_user=Depends(UserService.get_current_user), db: Session = Depends(get_db)):
    repo = ProcessedFileRepository(db)
    docs = repo.get_by_owner_id(current_user.id)
    return [{"id": doc.id, "name": doc.filename} for doc in docs]


@router.get("/{document_id}", response_model=DocumentResult, summary="получить содержимое документа")
def get_document(document_id: int, current_user=Depends(UserService.get_current_user), db: Session = Depends(get_db)):
    repo = ProcessedFileRepository(db)
    doc = repo.get(document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc.result


@router.get("/{document_id}/statistics", response_model=List[TermResponse], summary="получить статистику по документу")
def get_statistics(document_id: int, current_user=Depends(UserService.get_current_user), db: Session = Depends(get_db)):
    doc_repo = ProcessedFileRepository(db)
    stat_repo = WordStatRepository(db)
    doc = doc_repo.get(document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    stats = stat_repo.get_by_file_id(doc.file_id)
    return [{"word": s.term, "tf": s.tf, "idf": s.idf} for s in stats]


@router.delete("/{document_id}", response_model=MessageResponse, summary="удалить документ")
def delete_document(document_id: int, current_user=Depends(UserService.get_current_user),
                    db: Session = Depends(get_db)):
    repo = ProcessedFileRepository(db)
    doc = repo.get(document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    repo.delete(document_id)
    return {"message": "Document deleted"}
