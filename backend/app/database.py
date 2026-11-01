import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

import time
from sqlalchemy import text, inspect

if db_url.startswith("postgresql"):
    max_retries = 10
    connected = False
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(
                db_url,
                connect_args=connect_args,
                pool_pre_ping=True
            )
            with engine.connect() as conn:
                pass
            connected = True
            logger.info(f"Connected to primary database: {db_url}")
            break
        except Exception as e:
            if attempt < max_retries:
                logger.info(f"Database connection attempt {attempt}/{max_retries} failed ({e}). Retrying in 1s...")
                time.sleep(1)
            else:
                logger.warning(f"Could not connect to primary database after {max_retries} attempts ({e}). Falling back to SQLite: {settings.SQLITE_FALLBACK_URL}")
                db_url = settings.SQLITE_FALLBACK_URL
                connect_args = {"check_same_thread": False}
                engine = create_engine(
                    db_url,
                    connect_args=connect_args,
                    pool_pre_ping=True
                )
else:
    try:
        engine = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True
        )
        with engine.connect() as conn:
            pass
        logger.info(f"Connected to database: {db_url}")
    except Exception as e:
        logger.warning(f"Could not connect to database ({e}). Falling back to SQLite: {settings.SQLITE_FALLBACK_URL}")
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

    # Safe schema migration: ensure record_source column exists on existing tables across dialects
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())
            for tbl in [
                "applicants",
                "insured_assets",
                "quotes",
                "underwriting_decisions",
                "policies",
                "policy_events",
                "endorsements",
                "renewals"
            ]:
                if tbl not in existing_tables:
                    continue
                try:
                    cols = [c["name"] for c in inspector.get_columns(tbl)]
                    if "record_source" not in cols:
                        conn.execute(text(f"ALTER TABLE {tbl} ADD COLUMN record_source VARCHAR(30) DEFAULT 'USER' NOT NULL;"))
                        conn.commit()
                except Exception as inner_e:
                    logger.debug(f"Could not add record_source to {tbl}: {inner_e}")
    except Exception as e:
        logger.warning(f"Schema migration warning: {e}")

    logger.info("Database tables initialized successfully.")


def reset_db():
    init_db(drop_first=True)
