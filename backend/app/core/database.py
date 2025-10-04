"""
Database configuration and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


async def init_db():
    """Initialize database"""
    try:
        # Import all models to ensure they are registered
        from app.models import user, project, job, media, translation, voice, ethics
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def close_db():
    """Close database connections"""
    engine.dispose()
    logger.info("Database connections closed")