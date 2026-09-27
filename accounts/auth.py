"""JWT bearer authentication for Django Ninja endpoints."""

from ninja.security import HttpBearer

from accounts.repository import UserRepository
from core import mongo
from core.security import decode_access_token


class JWTAuth(HttpBearer):
    async def authenticate(self, request, token: str):
        user_id = decode_access_token(token)
        if user_id is None:
            return None
        repository = UserRepository(mongo.get_database())
        return await repository.find_by_id(user_id)
