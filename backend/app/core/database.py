import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Root directory for SQLite fallback database
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "discovery_engine.db"
SQLITE_FALLBACK_URL = f"sqlite:///{DB_PATH}"

def build_engine():
    """Builds the SQLAlchemy engine with graceful fallback to SQLite for local development."""
    db_url = settings.DATABASE_URL
    connect_args = {}

    try:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
            return create_engine(db_url, connect_args=connect_args)
        else:
            # Try PostgreSQL or specified DB
            engine = create_engine(db_url, pool_pre_ping=True)
            # Test engine dialect import
            _ = engine.dialect
            return engine
    except Exception as e:
        logger.warning(
            f"Could not initialize database with URL '{db_url}' ({e}). "
            f"Falling back to local SQLite at: {SQLITE_FALLBACK_URL}"
        )
        return create_engine(SQLITE_FALLBACK_URL, connect_args={"check_same_thread": False})

engine = build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency that provides a database session to FastAPI route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates database tables if they do not exist."""
    try:
        from backend.app.models.orm_models import (
            DataSource, RawPost, ExtractedEvidence, 
            ProblemCluster, ClusterEvidenceJunction, OpportunityArea
        )
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Error during init_db: {e}. Continuing with existing schema.")
