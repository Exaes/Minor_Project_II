"""
SQLAlchemy database engine and session management.

Uses SQLite by default for zero-dependency setup.
Swap to PostgreSQL by changing DATABASE_URL in .env.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import DATABASE_URL

# For SQLite, need check_same_thread=False for FastAPI async compatibility
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


def get_db():
    """Dependency — yields a database session, auto-closes on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Idempotent — safe to call multiple times."""
    # Import models so they register with Base.metadata
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
