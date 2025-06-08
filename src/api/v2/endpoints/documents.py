from fastapi import APIRouter

from settings import settings

router = APIRouter(
    prefix="/documents",
    responses={404: {"description": "Not found"}}
)


@router.get("/", summary="получить список документов")
async def get_documents():
    return {"id": 1, "title": "Название"}


@router.get("/{document_id}", summary="получить содержимое документа")
async def get_document(document_id: int):
    return {"status": document_id, "id": document_id}


@router.get("/{document_id}/statistics", summary="получить статистику по документу")
async def get_document_statistics(document_id: int):
    return {"status": document_id, "id": document_id}


@router.delete("/{document_id}", summary="удалить документ")
async def delete_document(document_id: int):
    return {"status": document_id, "id": document_id}
