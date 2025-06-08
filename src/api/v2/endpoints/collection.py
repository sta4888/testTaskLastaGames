from fastapi import APIRouter

from settings import settings

router = APIRouter(
    prefix="/collection",
    responses={404: {"description": "Not found"}}
)


@router.get("/", summary="получить список коллекций")
async def get_collections():
    return {"status": "OK"}


@router.get("/{collection_id}", summary="получить список документов коллекции")
async def get_collection(collection_id: int):
    return {"status": "OK", "id": collection_id}


@router.get("/{collection_id}/statistics", summary="получить статистику по коллекции")
async def get_collection_statistics(collection_id: int):
    return {"status": "OK", "id": collection_id}


@router.post("/{collection_id}/{document_id}", summary="добавить документ в коллекцию")
async def add_document_to_collection(collection_id: int, document_id: int):
    return {"status": "OK", "id": document_id, "collection_id": collection_id}


@router.delete("/{collection_id}/{document_id}", summary="удалить документ из коллекции")
async def delete_document_from_collection(collection_id: int, document_id: int):
    return {"status": "OK", "id": document_id, "collection_id": collection_id}
