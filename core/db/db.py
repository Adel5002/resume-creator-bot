import os

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import Annotated

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

async def get_session() -> None:
    async with AsyncSession(engine) as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]