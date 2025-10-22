from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
import os

# FORCE SQLITE - bypass settings temporarily
DATABASE_URL = "sqlite+aiosqlite:///./bookit.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()