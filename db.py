from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from functools import wraps
from configparser import ConfigParser
import asyncio

# Create an async engine and a sessionmaker
# Read the database URL from alembic.ini
config = ConfigParser()
config.read('./alembic.ini')
database_url = config.get('alembic', 'sqlalchemy.url').replace('postgresql://', 'postgresql+asyncpg://')

# Create an async engine and a sessionmaker
engine = create_async_engine(database_url, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

def db_session(func):
    @wraps(func)
    async def with_session(*args, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                kwargs['session'] = session
                result = await func(*args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e
    return with_session

def db_session_ro(func):
    @wraps(func)
    async def with_session(*args, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                kwargs['session'] = session
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                raise e
    return with_session