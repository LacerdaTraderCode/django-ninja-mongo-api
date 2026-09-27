"""Tests for registration, login, and the current-user endpoint."""

from ninja.testing import TestAsyncClient

from accounts.api import router

client = TestAsyncClient(router)


async def test_register_creates_a_new_user(mongo_database):
    response = await client.post(
        "/register",
        json={
            "email": "ana@example.com",
            "password": "correct-horse",
            "full_name": "Ana Silva",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "ana@example.com"
    assert "hashed_password" not in response.json()


async def test_register_rejects_a_duplicate_email(mongo_database):
    await client.post(
        "/register",
        json={
            "email": "ana@example.com",
            "password": "correct-horse",
            "full_name": "Ana Silva",
        },
    )

    response = await client.post(
        "/register",
        json={
            "email": "ana@example.com",
            "password": "another-password",
            "full_name": "Ana Silva",
        },
    )

    assert response.status_code == 409


async def test_login_returns_an_access_token_for_valid_credentials(mongo_database):
    await client.post(
        "/register",
        json={
            "email": "ana@example.com",
            "password": "correct-horse",
            "full_name": "Ana Silva",
        },
    )

    response = await client.post(
        "/login", json={"email": "ana@example.com", "password": "correct-horse"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_rejects_a_wrong_password(mongo_database):
    await client.post(
        "/register",
        json={
            "email": "ana@example.com",
            "password": "correct-horse",
            "full_name": "Ana Silva",
        },
    )

    response = await client.post(
        "/login", json={"email": "ana@example.com", "password": "wrong-password"}
    )

    assert response.status_code == 401


async def test_me_returns_the_authenticated_user(mongo_database):
    await client.post(
        "/register",
        json={
            "email": "ana@example.com",
            "password": "correct-horse",
            "full_name": "Ana Silva",
        },
    )
    login_response = await client.post(
        "/login", json={"email": "ana@example.com", "password": "correct-horse"}
    )
    access_token = login_response.json()["access_token"]

    response = await client.get("/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


async def test_me_rejects_a_missing_token(mongo_database):
    response = await client.get("/me")

    assert response.status_code == 401
