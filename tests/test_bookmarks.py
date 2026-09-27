"""Tests for bookmark creation, listing, updates, and ownership isolation."""

from ninja.testing import TestAsyncClient

from accounts.api import router as accounts_router
from bookmarks.api import router as bookmarks_router

accounts_client = TestAsyncClient(accounts_router)
bookmarks_client = TestAsyncClient(bookmarks_router)


async def _register_and_login(email: str) -> str:
    await accounts_client.post(
        "/register",
        json={"email": email, "password": "correct-horse", "full_name": "Test User"},
    )
    response = await accounts_client.post(
        "/login", json={"email": email, "password": "correct-horse"}
    )
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_create_and_list_bookmarks(mongo_database):
    token = await _register_and_login("reader@example.com")

    await bookmarks_client.post(
        "",
        json={
            "url": "https://example.com/article",
            "title": "An article",
            "tags": ["python"],
        },
        headers=_auth_headers(token),
    )
    response = await bookmarks_client.get("", headers=_auth_headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "An article"
    assert response.json()[0]["is_read"] is False


async def test_filter_bookmarks_by_tag(mongo_database):
    token = await _register_and_login("reader@example.com")
    await bookmarks_client.post(
        "",
        json={"url": "https://example.com/a", "title": "A", "tags": ["python"]},
        headers=_auth_headers(token),
    )
    await bookmarks_client.post(
        "",
        json={"url": "https://example.com/b", "title": "B", "tags": ["rust"]},
        headers=_auth_headers(token),
    )

    response = await bookmarks_client.get("?tag=rust", headers=_auth_headers(token))

    assert response.status_code == 200
    titles = [bookmark["title"] for bookmark in response.json()]
    assert titles == ["B"]


async def test_mark_a_bookmark_as_read(mongo_database):
    token = await _register_and_login("reader@example.com")
    created_response = await bookmarks_client.post(
        "",
        json={"url": "https://example.com/article", "title": "An article", "tags": []},
        headers=_auth_headers(token),
    )
    created = created_response.json()

    response = await bookmarks_client.patch(
        f"/{created['id']}", json={"is_read": True}, headers=_auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True


async def test_delete_a_bookmark(mongo_database):
    token = await _register_and_login("reader@example.com")
    created_response = await bookmarks_client.post(
        "",
        json={"url": "https://example.com/article", "title": "An article", "tags": []},
        headers=_auth_headers(token),
    )
    created = created_response.json()

    delete_response = await bookmarks_client.delete(
        f"/{created['id']}", headers=_auth_headers(token)
    )
    get_response = await bookmarks_client.get(f"/{created['id']}", headers=_auth_headers(token))

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


async def test_a_user_cannot_see_another_users_bookmarks(mongo_database):
    owner_token = await _register_and_login("owner@example.com")
    intruder_token = await _register_and_login("intruder@example.com")
    created_response = await bookmarks_client.post(
        "",
        json={"url": "https://example.com/private", "title": "Private", "tags": []},
        headers=_auth_headers(owner_token),
    )
    created = created_response.json()

    response = await bookmarks_client.get(
        f"/{created['id']}", headers=_auth_headers(intruder_token)
    )

    assert response.status_code == 404


async def test_unknown_bookmark_id_returns_not_found_instead_of_error(mongo_database):
    token = await _register_and_login("reader@example.com")

    response = await bookmarks_client.get("/not-a-valid-object-id", headers=_auth_headers(token))

    assert response.status_code == 404
