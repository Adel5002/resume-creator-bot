from fastapi import HTTPException
from typing import Sequence, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core import ResumeVersion, Resume, User, Profile
from core.schemas.profile_schema import ProfileBase
from core.schemas.resume_schema import ResumeCreate, ResumeUpdate, ResumeBase
from core.schemas.resume_version_schema import ResumeVersionBase


class ResumeService:

    @staticmethod
    async def create_resume_version(
            resume_data: Any, session: AsyncSession, resume_id: int, version: int = 1
    ) -> ResumeVersion:

        version_data = ResumeVersionBase(
            **resume_data.model_dump(exclude={"version", "resume_id"}),
            version=version,
            resume_id=resume_id
        )

        profile = ProfileBase(**resume_data.model_dump())

        version_model = ResumeVersion(**version_data.model_dump())

        session.add(version_model)
        await session.flush()
        profile_model = Profile(**profile.model_dump(), version_id=version_model.id)
        session.add(profile_model)

        await session.commit()
        await session.refresh(version_model)
        await session.refresh(profile_model)

        return version_model

    @staticmethod
    async def create(data: ResumeCreate, session: AsyncSession) -> Resume:
        user_exists = await session.scalar(select(User).where(User.telegram_id == data.user_id))

        if not user_exists:
            raise HTTPException(status_code=404, detail="User does not exist")

        resume = ResumeBase(**data.model_dump(exclude={"user_id"}))

        resume = Resume(**resume.model_dump(),user_id=data.user_id)
        session.add(resume)
        await session.commit()
        await session.refresh(resume)

        await ResumeService.create_resume_version(data, session, resume.id)

        return resume

    @staticmethod
    async def update(resume_id: int, data: ResumeUpdate, session: AsyncSession) -> Resume:
        resume = await session.scalar(
            select(Resume)
            .options(joinedload(Resume.versions).joinedload(ResumeVersion.profile))
            .where(Resume.id == resume_id)
        )
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        max_version = max(resume.versions, key=lambda version: version.version)
        await ResumeService.create_resume_version(
            data, session, resume_id=resume.id, version=max_version.version + 1
        )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resume, field, value)
        await session.commit()
        await session.refresh(resume)

        return resume

    @staticmethod
    async def get_by_id(resume_id: int, session: AsyncSession) -> Resume:
        resume = await session.get(Resume, resume_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        return resume

    @staticmethod
    async def list_by_user(user_id: int, session: AsyncSession) -> Sequence[Resume]:
        results = await session.scalars(
            select(Resume).where(Resume.user_id == user_id)
        )
        resumes = results.all()

        if not resumes:
            raise HTTPException(status_code=404, detail="User has no resumes yet")

        return resumes

    @staticmethod
    async def delete(resume_id: int, session: AsyncSession) -> None:
        resume = await ResumeService.get_by_id(resume_id, session)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        await session.delete(resume)
        await session.commit()
