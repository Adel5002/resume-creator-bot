from fastapi import APIRouter

from core.schemas.user_schema import UserRead, UserCreate
from core.db.db import SessionDep
from core.services.user_service import UserService

router = APIRouter()

@router.post("/create/", response_model=UserRead)
async def create(user_data: UserCreate, sessions: SessionDep):
    return await UserService.create(user_data=user_data, session=sessions)