import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE = os.getenv("DATABASE")


engine = create_async_engine(DATABASE)

async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
