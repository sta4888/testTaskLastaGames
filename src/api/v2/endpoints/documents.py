from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import WordStat
from repositories.processed_file import ProcessedFileRepository
from repositories.word_stat import WordStatRepository
from schemas.document import DocumentListItem, DocumentResult, MessageResponse, DocumentHuffmanResult
from schemas.schemas import TermResponse
from services.user import UserService
from utils.haffman import build_huffman_tree, get_codes, encode

router = APIRouter(prefix="/documents")


@router.get("/", response_model=List[DocumentListItem], summary="получить список документов")
def get_documents(current_user=Depends(UserService.get_current_user), db: Session = Depends(get_db)):
    repo = ProcessedFileRepository(db)
    docs = repo.get_by_owner_id(current_user.id)
    return [DocumentListItem(id=doc.id, name=doc.filename) for doc in docs]


@router.get("/{document_id}", response_model=DocumentResult, summary="получить содержимое документа")
def get_document(document_id: int, current_user=Depends(UserService.get_current_user), db: Session = Depends(get_db)):
    repo = ProcessedFileRepository(db)
    doc = repo.get(document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        with open(doc.file_path, "r", encoding="utf-8") as f:
            file_text = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on disk")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    return DocumentResult(
        lines_count=doc.result.get("lines_count"),
        text=file_text
    )


@router.get("/{document_id}/statistics", response_model=List[TermResponse], summary="получить статистику по документу")
def get_statistics(document_id: int, current_user=Depends(UserService.get_current_user), db: Session = Depends(get_db)):
    doc_repo = ProcessedFileRepository(db)
    stat_repo = WordStatRepository(db)
    doc = doc_repo.get(document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    stats = stat_repo.get_by_file_id(doc.file_id)
    return [TermResponse(word=s.term, tf=s.tf, idf=s.idf) for s in stats]


@router.delete("/{document_id}", response_model=MessageResponse, summary="удалить документ")
def delete_document(document_id: int, current_user=Depends(UserService.get_current_user),
                    db: Session = Depends(get_db)):
    repo = ProcessedFileRepository(db)
    doc = repo.get(document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    db.query(WordStat).filter(WordStat.file_id == doc.file_id).delete()

    repo.delete(document_id)
    db.commit()
    return MessageResponse(message="Document deleted")


@router.get(
    "/{document_id}/huffman",
    response_model=DocumentHuffmanResult,
    summary=" получить содержимое документа, закодированное Кодом Хаффмана"
)
def get_document_huffman(
        document_id: int,
        current_user=Depends(UserService.get_current_user),
        db: Session = Depends(get_db)
):
    repo = ProcessedFileRepository(db)
    doc = repo.get(document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        with open(doc.file_path, "r", encoding="utf-8") as f:
            file_text = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on disk")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    tree = build_huffman_tree(file_text)
    codes = get_codes(tree)
    encoded = encode(file_text, codes)
    return DocumentHuffmanResult(
        text=encoded
    )
