import json
from datetime import datetime, UTC, timezone
from pydantic import BaseModel, ConfigDict

from core import Resume
from core.models.resume import ResumeCreationMode
from core.schemas.resume_version_schema import ResumeVersionCreate, ResumeVersionUpdate, ResumeVersionRead


class ResumeBase(BaseModel):
    title: str
    creation_mode: ResumeCreationMode = ResumeCreationMode.NEW
    created_at: datetime = datetime.now(UTC)

class ResumeCreate(ResumeBase, ResumeVersionCreate):
    user_id: int
    resume_id: int | None = None
    version: int | None = None

class ResumeUpdate(ResumeVersionUpdate):
    title: str | None = None
    creation_mode: ResumeCreationMode | None = None

class ResumeRead(ResumeBase):
    id: int
    user_id: int
    versions: list["ResumeVersionRead"] = []

    model_config = ConfigDict(from_attributes=True)

