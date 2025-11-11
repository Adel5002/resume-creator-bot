from fastapi import APIRouter

from core.schemas.user_schema import UserRead, UserCreate, UserUpdate
from core.db.db import SessionDep
from core.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def get_all_users(session: SessionDep):
    users = await UserService.all(session=session)
    return users

@router.post("/create/", response_model=UserRead)
async def create(user_data: UserCreate, session: SessionDep):
    return await UserService.create(user_data=user_data, session=session)

@router.get("/get/{telegram_id}/", response_model=UserRead)
async def get_user_by_telegram_id(telegram_id: int, session: SessionDep):
    return await UserService.get_by_telegram_id(telegram_id=telegram_id, session=session)

@router.patch("/update/{user_id}/", response_model=UserRead)
async def update_user(user_id: int, user_data: UserUpdate, session: SessionDep):
    return await UserService.update(user_id=user_id, user_data=user_data, session=session)

@router.delete("/delete/{user_id}/")
async def delete_user(user_id: int, session: SessionDep):
    await UserService.delete(user_id=user_id, session=session)
    return {"detail": "User deleted"}
