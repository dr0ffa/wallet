import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os


#DATABASE_URL = "postgresql+asyncpg://user:password@wallet_db:5432/wallet_db"

load_dotenv()  # автоматически ищет .env в корне проекта

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Make sure .env file exists and is loaded.")



engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

#@asynccontextmanager
async def get_db_context():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise