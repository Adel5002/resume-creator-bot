from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    name: str | None = None
    position: str | None = None
    contacts: dict | None = None
    summary: str | None = None
    skills: list[str] | None = None
    experience: list[dict] | None = None
    education: list[dict] | None = None


class ProfileCreate(ProfileBase):
    version_id: int


class ProfileUpdate(BaseModel):
    name: str | None = None
    position: str | None = None
    contacts: dict | None = None
    summary: str | None = None
    skills: list[str] | None = None
    experience: list[dict] | None = None
    education: list[dict] | None = None
    instructions: str | None = None


class ProfileRead(ProfileBase):
    id: int
    version_id: int

    model_config = ConfigDict(from_attributes=True)
