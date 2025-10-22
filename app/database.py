from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from app.config import settings

def get_engine():
    database_url = settings.DATABASE_URL
    
    print(f"Environment: {settings.ENV}")
    print(f"Database URL: {database_url}")
    
    if "sqlite" in database_url:
        print("Configuring SQLite database...")
        return create_async_engine(
            database_url,
            echo=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
    else:
        if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            print(f"Converted to asyncpg URL: {database_url}")
        
        print("Configuring PostgreSQL database...")
        return create_async_engine(
            database_url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
        )

# Create engine using the function
engine = get_engine()

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"Database tables created successfully in {settings.ENV} environment!")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()