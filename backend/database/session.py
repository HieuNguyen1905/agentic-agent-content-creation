"""Database session and connection management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
import os

from database.models import Base

# Database URL - can be configured via environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent.parent / '.agent_data' / 'blog.db'}"
)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # For PostgreSQL or other databases
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    # Ensure directory exists
    db_path = Path(__file__).parent.parent / '.agent_data'
    db_path.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized: {DATABASE_URL}")


@contextmanager
def get_db() -> Session:
    """
    Provide a transactional scope for database operations.
    
    Usage:
        with get_db() as db:
            db.query(BlogPost).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_dependency():
    """
    FastAPI dependency for database sessions.
    
    Usage:
        @router.get("/posts")
        def get_posts(db: Session = Depends(get_db_dependency)):
            return db.query(BlogPost).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
