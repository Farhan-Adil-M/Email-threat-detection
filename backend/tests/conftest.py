import os
import shutil
from pathlib import Path

# Use SQLite for tests to avoid requiring a running PostgreSQL instance.
os.environ["DATABASE_URL"] = "sqlite:///./backend/tests/test.db"
os.environ["EVIDENCE_STORAGE_PATH"] = "./backend/tests/storage"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models.base import Base

engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_storage():
    storage = Path(os.environ["EVIDENCE_STORAGE_PATH"])
    if storage.exists():
        shutil.rmtree(storage)
    storage.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture
def client():
    return TestClient(app)
