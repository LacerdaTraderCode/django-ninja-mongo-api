"""Data access for user accounts, backed by MongoDB."""

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    """Wraps the `users` collection so callers never touch Mongo directly."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database["users"]

    async def find_by_email(self, email: str) -> dict | None:
        return await self._collection.find_one({"email": email})

    async def find_by_id(self, user_id: str) -> dict | None:
        try:
            object_id = ObjectId(user_id)
        except InvalidId:
            return None
        return await self._collection.find_one({"_id": object_id})

    async def create(self, email: str, hashed_password: str, full_name: str) -> dict:
        document = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
        }
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document
