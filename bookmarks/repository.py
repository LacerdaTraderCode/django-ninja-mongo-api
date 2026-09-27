"""Data access for bookmarks, backed by MongoDB.

Every query here is scoped by `owner_id`, on purpose: this is the one place
that guarantees one account can never read or modify another account's
bookmarks, so it is worth keeping centralized rather than repeated in the
API layer.
"""

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class BookmarkRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database["bookmarks"]

    async def create(
        self, owner_id: str, url: str, title: str, tags: list[str], notes: str | None
    ) -> dict:
        document = {
            "owner_id": owner_id,
            "url": url,
            "title": title,
            "tags": tags,
            "notes": notes,
            "is_read": False,
            "saved_at": datetime.now(timezone.utc),
        }
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def list_for_owner(
        self, owner_id: str, tag: str | None, is_read: bool | None
    ) -> list[dict]:
        query: dict = {"owner_id": owner_id}
        if tag is not None:
            query["tags"] = tag
        if is_read is not None:
            query["is_read"] = is_read
        cursor = self._collection.find(query).sort("saved_at", -1)
        return [document async for document in cursor]

    async def find_owned(self, bookmark_id: str, owner_id: str) -> dict | None:
        object_id = self._parse_object_id(bookmark_id)
        if object_id is None:
            return None
        return await self._collection.find_one({"_id": object_id, "owner_id": owner_id})

    async def update_owned(self, bookmark_id: str, owner_id: str, changes: dict) -> dict | None:
        object_id = self._parse_object_id(bookmark_id)
        if object_id is None:
            return None
        if changes:
            await self._collection.update_one(
                {"_id": object_id, "owner_id": owner_id}, {"$set": changes}
            )
        return await self.find_owned(bookmark_id, owner_id)

    async def delete_owned(self, bookmark_id: str, owner_id: str) -> bool:
        object_id = self._parse_object_id(bookmark_id)
        if object_id is None:
            return False
        result = await self._collection.delete_one({"_id": object_id, "owner_id": owner_id})
        return result.deleted_count == 1

    @staticmethod
    def _parse_object_id(raw_id: str) -> ObjectId | None:
        try:
            return ObjectId(raw_id)
        except InvalidId:
            return None
