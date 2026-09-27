"""HTTP endpoints for registration, login, and the current-user profile."""

from ninja import Router, Status

from accounts.auth import JWTAuth
from accounts.repository import UserRepository
from accounts.schemas import (
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from core import mongo
from core.security import create_access_token, hash_password, verify_password

router = Router(tags=["accounts"])


def _serialize_user(user: dict) -> UserOut:
    return UserOut(id=str(user["_id"]), email=user["email"], full_name=user["full_name"])


@router.post("/register", response={201: UserOut, 409: ErrorResponse})
async def register(request, payload: RegisterRequest):
    repository = UserRepository(mongo.get_database())
    if await repository.find_by_email(payload.email) is not None:
        return Status(409, ErrorResponse(detail="An account with this email already exists."))
    hashed_password = hash_password(payload.password)
    user = await repository.create(payload.email, hashed_password, payload.full_name)
    return Status(201, _serialize_user(user))


@router.post("/login", response={200: TokenResponse, 401: ErrorResponse})
async def login(request, payload: LoginRequest):
    repository = UserRepository(mongo.get_database())
    user = await repository.find_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["hashed_password"]):
        return Status(401, ErrorResponse(detail="Invalid email or password."))
    access_token = create_access_token(subject=str(user["_id"]))
    return Status(200, TokenResponse(access_token=access_token))


@router.get("/me", response=UserOut, auth=JWTAuth())
async def me(request):
    return _serialize_user(request.auth)
