"""HTTP endpoints for creating, listing, updating, and deleting bookmarks."""

from ninja import Query, Router, Status

from accounts.auth import JWTAuth
from bookmarks.repository import BookmarkRepository
from bookmarks.schemas import BookmarkCreate, BookmarkOut, BookmarkUpdate, ErrorResponse
from core import mongo

router = Router(tags=["bookmarks"], auth=JWTAuth())


def _serialize(document: dict) -> BookmarkOut:
    return BookmarkOut(
        id=str(document["_id"]),
        url=document["url"],
        title=document["title"],
        tags=document["tags"],
        notes=document.get("notes"),
        is_read=document["is_read"],
        saved_at=document["saved_at"].isoformat(),
    )


@router.post("", response={201: BookmarkOut})
async def create_bookmark(request, payload: BookmarkCreate):
    repository = BookmarkRepository(mongo.get_database())
    owner_id = str(request.auth["_id"])
    document = await repository.create(
        owner_id, payload.url, payload.title, payload.tags, payload.notes
    )
    return Status(201, _serialize(document))


@router.get("", response=list[BookmarkOut])
async def list_bookmarks(
    request, tag: str | None = Query(None), is_read: bool | None = Query(None)
):
    repository = BookmarkRepository(mongo.get_database())
    owner_id = str(request.auth["_id"])
    documents = await repository.list_for_owner(owner_id, tag, is_read)
    return [_serialize(document) for document in documents]


@router.get("/{bookmark_id}", response={200: BookmarkOut, 404: ErrorResponse})
async def get_bookmark(request, bookmark_id: str):
    repository = BookmarkRepository(mongo.get_database())
    owner_id = str(request.auth["_id"])
    document = await repository.find_owned(bookmark_id, owner_id)
    if document is None:
        return Status(404, ErrorResponse(detail="Bookmark not found."))
    return Status(200, _serialize(document))


@router.patch("/{bookmark_id}", response={200: BookmarkOut, 404: ErrorResponse})
async def update_bookmark(request, bookmark_id: str, payload: BookmarkUpdate):
    repository = BookmarkRepository(mongo.get_database())
    owner_id = str(request.auth["_id"])
    changes = payload.model_dump(exclude_unset=True)
    document = await repository.update_owned(bookmark_id, owner_id, changes)
    if document is None:
        return Status(404, ErrorResponse(detail="Bookmark not found."))
    return Status(200, _serialize(document))


@router.delete("/{bookmark_id}", response={204: None, 404: ErrorResponse})
async def delete_bookmark(request, bookmark_id: str):
    repository = BookmarkRepository(mongo.get_database())
    owner_id = str(request.auth["_id"])
    deleted = await repository.delete_owned(bookmark_id, owner_id)
    if not deleted:
        return Status(404, ErrorResponse(detail="Bookmark not found."))
    return Status(204, None)
