"""Pydantic schemas for the bookmarks module."""

from ninja import Schema
from pydantic import Field


class BookmarkCreate(Schema):
    url: str
    title: str
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class BookmarkUpdate(Schema):
    title: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
    is_read: bool | None = None


class BookmarkOut(Schema):
    id: str
    url: str
    title: str
    tags: list[str]
    notes: str | None = None
    is_read: bool
    saved_at: str


class ErrorResponse(Schema):
    detail: str
