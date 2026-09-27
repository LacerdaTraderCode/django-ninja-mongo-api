"""Async MongoDB client shared across the application.

`get_database` is called fresh by every repository instead of being injected
through a framework-level dependency system, which keeps the module easy to
monkeypatch in tests (see tests/conftest.py).
"""

from django.conf import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None


def get_database() -> AsyncIOMotorDatabase:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client[settings.MONGO_DB_NAME]
