"""Pydantic schemas for the accounts module."""

from ninja import Schema


class RegisterRequest(Schema):
    email: str
    password: str
    full_name: str


class LoginRequest(Schema):
    email: str
    password: str


class TokenResponse(Schema):
    access_token: str
    token_type: str = "bearer"


class UserOut(Schema):
    id: str
    email: str
    full_name: str


class ErrorResponse(Schema):
    detail: str
