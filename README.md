# Django Ninja + MongoDB API

A REST API boilerplate that pairs [Django Ninja](https://django-ninja.dev/) with MongoDB instead of Django's traditional ORM — JWT authentication, async views end to end, and a small but complete bookmarks (reading list) resource used as a worked example.

This is the NoSQL counterpart to a FastAPI + PostgreSQL boilerplate: same kind of problem, a different stack, so the trade-offs are easy to compare side by side.

## Why MongoDB instead of Django's ORM

Django ships with a database-agnostic ORM built around relational databases. This project deliberately does not use it for application data: Django only supplies routing, settings, and the ASGI entrypoint, while every read and write goes through [Motor](https://motor.readthedocs.io/), the official async MongoDB driver. A local SQLite file is configured only because Django's internals expect a `DATABASES` entry — no application code ever touches it.

## Stack

- **Django Ninja** — routing, request validation, and automatic OpenAPI docs
- **MongoDB** via **Motor** — async driver, no ORM in between
- **PyJWT** + **argon2-cffi** — token issuance and password hashing
- **Pytest** + **mongomock-motor** — a hermetic test suite that needs no running database

## Features

- Email/password registration and login, with JWT access tokens
- Bookmark CRUD: create, list with tag/read-state filters, update, delete
- Every bookmark is scoped to its owner — one account can never read or modify another account's data
- Fully async request handlers, with a repository layer decoupled from the API layer
- CI running the full test suite on every push

## Project layout

```
config/       Django settings, URL routing, ASGI entrypoint
core/         Mongo client and security (hashing, JWT) helpers shared across modules
accounts/     Registration, login, and JWT authentication
bookmarks/    The example resource: schemas, repository, and endpoints
tests/        Pytest suite, backed by an in-memory Mongo double
```

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then point MONGO_URI at a running MongoDB instance
python manage.py runserver
```

Interactive API docs are served at `/api/docs`.

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

No MongoDB instance is required: the test suite swaps in an in-memory double for every test, including a check that one account can never read another account's bookmarks.

## License

MIT — see [LICENSE](LICENSE).
