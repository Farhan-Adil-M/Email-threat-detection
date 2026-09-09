import os
import shutil
from pathlib import Path

# Determine project paths relative to this file: backend/tests/conftest.py
TEST_DIR = Path(__file__).resolve().parent
STORAGE_DIR = TEST_DIR / "storage"
DB_PATH = TEST_DIR / "test.db"

# Use SQLite for tests to avoid requiring a running PostgreSQL instance.
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["EVIDENCE_STORAGE_PATH"] = str(STORAGE_DIR)
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models.base import Base
# Register every mapped table for metadata-based SQLite tests.
from app.models.attachment import Attachment  # noqa: F401
from app.models.audit import AuditEvent  # noqa: F401
from app.models.auth_result import AuthenticationResult  # noqa: F401
from app.models.email import EmailMessage  # noqa: F401
from app.models.finding import Finding  # noqa: F401
from app.models.graph import GraphEdge, GraphNode  # noqa: F401
from app.models.ml_assessment import MLAssessment  # noqa: F401
from app.models.received_hop import ReceivedHop  # noqa: F401
from app.models.risk_assessment import RiskAssessment  # noqa: F401
from app.models.threat_intel import ThreatIntelResult  # noqa: F401
from app.models.url_indicator import URLIndicator  # noqa: F401

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
    # Ensure the tests directory exists for the SQLite file.
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_storage():
    if STORAGE_DIR.exists():
        shutil.rmtree(STORAGE_DIR)
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture
def client():
    return TestClient(app)
