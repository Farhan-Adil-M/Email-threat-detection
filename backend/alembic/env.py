from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.config import settings
from app.models.base import Base

# Import all models so Alembic can discover them
from app.models.audit import AuditEvent  # noqa: F401
from app.models.auth_result import AuthenticationResult  # noqa: F401
from app.models.case import Case  # noqa: F401
from app.models.email import EmailMessage  # noqa: F401
from app.models.evidence import EvidenceObject  # noqa: F401
from app.models.finding import Finding  # noqa: F401
from app.models.received_hop import ReceivedHop  # noqa: F401
from app.models.attachment import Attachment  # noqa: F401
from app.models.url_indicator import URLIndicator  # noqa: F401
from app.models.threat_intel import ThreatIntelResult  # noqa: F401
from app.models.ml_assessment import MLAssessment  # noqa: F401
from app.models.risk_assessment import RiskAssessment  # noqa: F401
from app.models.graph import GraphNode, GraphEdge  # noqa: F401
from app.models.campaign import Campaign, CampaignMembership, MitreMapping  # noqa: F401
from app.models.case_note import CaseNote  # noqa: F401

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url from environment
config.set_main_option("sqlalchemy.url", settings.get_database_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
