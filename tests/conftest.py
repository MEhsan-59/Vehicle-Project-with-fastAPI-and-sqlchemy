# tests/conftest.py
import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-0123456789")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models import Base
from account_repository import AccountRepository
from account_manager import AccountManager
from part_repository import PartRepository
from part_manager import PartManager
from car_repository import CarRepository
from car_manager import CarManager


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def account_repo(db_session):
    return AccountRepository(db_session)


@pytest.fixture()
def account_manager(account_repo):
    return AccountManager(account_repo)


@pytest.fixture()
def part_repo(db_session):
    return PartRepository(db_session)


@pytest.fixture()
def part_manager(part_repo):
    return PartManager(part_repo)


@pytest.fixture()
def car_repo(db_session):
    return CarRepository(db_session)


@pytest.fixture()
def car_manager(car_repo):
    return CarManager(car_repo)


@pytest.fixture()
def client(db_session):
    from fastapi.testclient import TestClient
    from main import app
    from database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()