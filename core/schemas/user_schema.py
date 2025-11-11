from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict
from typing import List

from core.schemas.resume_schema import ResumeRead


class UserBase(BaseModel):
    name: str
    created_at: datetime = datetime.now(UTC)

class UserCreate(UserBase):
    telegram_id: int

class UserUpdate(BaseModel):
    name: str | None = None
    last_seen: datetime | None = None

class UserRead(UserBase):
    telegram_id: int
    last_seen: datetime | None
    resumes: List["ResumeRead"] | None

    model_config = ConfigDict(from_attributes=True)
