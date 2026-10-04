# Vehicle Manager API

A layered vehicle maintenance API built with **FastAPI**, **SQLAlchemy**, and **Pydantic**.
Rewritten from an earlier command-line Vehicle Maintenance app.

## Current Status

- `POST /create_account` — create a new account (passwords are bcrypt-hashed)
- `POST /login_account` — log in and receive a JWT access token
- `GET /me` — logged-in user's profile (requires `Authorization: Bearer <token>`)
- `GET /health` — health check

Models for `Vehicle`, `Part`, `Maintenance` and `History` are ready; their APIs are next.

## Quick Start

```
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own values:

```
DATABASE_URL=sqlite:///./Vehicle_app.db
SECRET_KEY=your-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Create the tables, then start the server:

```
python create_table.py
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000/docs> for the interactive Swagger UI.

## Testing

```
pytest
```

## Project Structure

```
main.py                 FastAPI app and endpoints
schema.py               Pydantic request/response schemas
models.py               SQLAlchemy tables
account_manager.py      Account business logic
account_repository.py   Account database access
auth.py                 JWT create/decode
security.py             bcrypt password hashing
config.py               Settings from .env
database.py             Engine and sessions
logger_setup.py         Logging
create_table.py         Creates the tables
tests/                  pytest tests
```
