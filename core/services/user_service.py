from fastapi import HTTPException
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User
from core.schemas.user_schema import UserCreate, UserUpdate


class UserService:
    @staticmethod
    async def create(user_data: UserCreate, session: AsyncSession) -> User:
        user_exists = await session.scalar(
            select(User).where(User.telegram_id == user_data.telegram_id)
        )

        if user_exists:
            raise HTTPException(status_code=409, detail="User already exists")

        user = User(**user_data.model_dump())

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user


    @staticmethod
    async def get_by_telegram_id(telegram_id: int, session: AsyncSession) -> User:
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    @staticmethod
    async def update(user_id: int, user_data: UserUpdate, session: AsyncSession) -> User:
        user = await session.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_values = user_data.model_dump(exclude_unset=True)
        for attr, value in update_values.items():
            setattr(user, attr, value)

        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(user_id: int, session: AsyncSession) -> None:
        user = await session.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await session.delete(user)
        await session.commit()

    @staticmethod
    async def all(session: AsyncSession) -> Sequence[User]:
        result = await session.scalars(select(User))
        users = result.all()

        if not users:
            raise HTTPException(status_code=404, detail="There are no users yet")

        return users