import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info(f"Connected to database: {db_url}")
except Exception as e:
    logger.warning(f"Could not connect to primary database ({e}). Falling back to SQLite: {settings.SQLITE_FALLBACK_URL}")
    db_url = settings.SQLITE_FALLBACK_URL
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(drop_first: bool = False):
    from backend.app.models import (
        applicant,
        asset,
        product,
        risk_factor,
        quote,
        underwriting,
        policy,
        endorsement,
        renewal,
        anomaly,
        audit
    )
    if drop_first:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


def reset_db():
    init_db(drop_first=True)
