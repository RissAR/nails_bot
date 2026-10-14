import logging
import os
import shutil
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings

logger = logging.getLogger(__name__)

# Ensure data directory exists and migrate existing database if needed
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.split(":///")[-1]
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    root_db = os.path.abspath("./nails_salon.db")
    target_db = os.path.abspath(db_path)
    if os.path.exists(root_db) and not os.path.exists(target_db) and root_db != target_db:
        shutil.copy2(root_db, target_db)
        logger.info("Migrated existing database from %s to %s", root_db, target_db)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope around a series of operations."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
