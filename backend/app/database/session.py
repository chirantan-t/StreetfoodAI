"""
Database session and initialization manager for StreetFoodAI SQLite store.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.database.models import Base

DEFAULT_DB_URL = "sqlite:///./streetfood_history.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes schema and tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI dependency for database session lifecycle."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
