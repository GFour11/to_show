from db.postgres_connection import async_session
from postgres_connection import engine
from postgres_models import Base, Proxies
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio


async def create_models():
    """Created all models in db"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_models())
