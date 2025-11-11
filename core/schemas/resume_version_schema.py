from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict


class ResumeVersionBase(BaseModel):
    version: int
    resume_id: int
    extra_info_json: dict | None = None
    path_to_html: str | None = None
    path_to_image: str | None = None
    path_to_pdf: str | None = None


class ResumeVersionCreate(ResumeVersionBase):
    resume_id: int


class ResumeVersionUpdate(BaseModel):
    version: int | None = None
    extra_info_json: dict | None = None
    path_to_html: str | None = None
    path_to_image: str | None = None
    path_to_pdf: str | None = None


class ResumeVersionRead(ResumeVersionBase):
    id: int
    resume_id: int
    created_at: datetime = datetime.now(UTC)

    model_config = ConfigDict(from_attributes=True)
