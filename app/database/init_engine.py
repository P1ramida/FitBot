from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from ..config import settings


async_engine = create_async_engine(url=settings.DATABASE_URL)

async_session = async_sessionmaker(async_engine, class_=AsyncSession)
