from fastapi import HTTPException
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas.user_schema import UserCreate
from core.models.user import User


class UserService:
    @staticmethod
    async def create(user_data: UserCreate, session: AsyncSession) -> User:
        user_exists = await session.scalar(
            select(User)
            .where(User.telegram_id == user_data.telegram_id)
        )

        if user_exists:
            raise HTTPException(status_code=409, detail="User already exists")

        user = User(**user_data.model_dump())

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def all(session: AsyncSession) -> Sequence[User]:
        users = await session.scalars(select(User))

        if not users:
            raise HTTPException(status_code=404, detail="There no users yet")

        return users.all()