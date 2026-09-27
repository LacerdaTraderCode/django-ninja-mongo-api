"""Shared pytest fixtures for the test suite."""

import pytest
from mongomock_motor import AsyncMongoMockClient

from core import mongo


@pytest.fixture
def mongo_database(monkeypatch):
    """Swap in an isolated, in-memory MongoDB double for a single test."""
    client = AsyncMongoMockClient()
    database = client["test_database"]
    monkeypatch.setattr(mongo, "get_database", lambda: database)
    return database
