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
# async def add_proxies():
#     proxies = [Proxies(proxy="http://snzakpfz:zdawuph7260g@107.172.163.27:6543"),
#                Proxies(proxy="http://snzakpfz:zdawuph7260g@207.244.217.165:6712"),
#                Proxies(proxy="http://snzakpfz:zdawuph7260g@198.23.239.134:6540")]
#
#
#     from postgres_connection import async_session
#     async with async_session() as session:  # Додано async with
#         session.add_all(proxies)
#         await session.commit()
#
# asyncio.run(add_proxies())