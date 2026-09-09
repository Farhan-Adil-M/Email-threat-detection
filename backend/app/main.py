from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.api.v1.router import api_router
from app.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.database import engine
from app.models.base import Base

logger = logging.getLogger(__name__)
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized.")
    except OperationalError as exc:
        logger.warning("Database unavailable at startup: %s", exc)
    yield
    engine.dispose()


app = FastAPI(
    title="SENTINEL — Email Threat Detection & Forensics",
    description="SIH 26106 forensic investigation platform",
    version="0.1.0",
    lifespan=lifespan,
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
