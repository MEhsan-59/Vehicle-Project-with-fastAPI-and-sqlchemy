# Vehicle Manager API

A layered vehicle maintenance API built with **FastAPI**, **SQLAlchemy**, and **Pydantic**.
Rewritten from an earlier command-line Vehicle Maintenance app.

## Current Status

- `POST /create_account` — create a new account (passwords are bcrypt-hashed)
- `POST /login_account` — log in and receive a JWT access token
- `GET /me` — logged-in user's profile (requires `Authorization: Bearer <token>`)
- `GET /health` — health check
- `POST /parts` — add a new part type (409 if the name already exists)
- `PUT /parts/{part}` — update the settings of an existing part type (404 if missing)
- `DELETE /parts/{part}` — delete a part type (404 if missing, 409 if a car still uses it)
- `GET /parts` — list all part types

- `POST /cars` add a car
- `DELETE /cars/{car_no}` delete a car
- `PUT /cars/{car_no}/km` update the car's km (cannot go down)
- `PUT /cars/{car_no}/parts/{part}` add or update a part on a car (next km and date are calculated, history is saved)

Next: listing cars and maintenance details, and a history endpoint.

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
part_manager.py         Part type add/update/delete logic
part_repository.py      Part type database access
car_manager.py           Car add, delete and km update logic
car_repository.py        Car database access
maintenance_manager.py   Update a part on a car
maintenance_repository.py  Maintenance database access
helper.py                Static helpers
auth.py                 JWT create/decode
security.py             bcrypt password hashing
config.py               Settings from .env
database.py             Engine and sessions
logger_setup.py         Logging
create_table.py         Creates the tables
tests/                  pytest tests
```