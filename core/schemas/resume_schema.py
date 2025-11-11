
from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict

from core import ResumeVersion, Profile
from core.models.resume import ResumeCreationMode
from core.schemas.profile_schema import ProfileCreate, ProfileUpdate
from core.schemas.resume_version_schema import ResumeVersionCreate, ResumeVersionUpdate, ResumeVersionRead


class ResumeBase(BaseModel):
    title: str
    creation_mode: ResumeCreationMode = ResumeCreationMode.NEW
    created_at: datetime = datetime.now(UTC)

class ResumeCreate(ResumeBase, ResumeVersionCreate, ProfileCreate):
    user_id: int
    resume_id: int | None = None
    version: int | None = None
    version_id: int | None = None

class ResumeUpdate(ResumeVersionUpdate, ProfileUpdate):
    title: str | None = None
    creation_mode: ResumeCreationMode | None = None

class ResumeRead(ResumeBase):
    id: int
    user_id: int
    versions: list["ResumeVersionRead"] = []

    model_config = ConfigDict(from_attributes=True)


