import json
import os

from fastapi import HTTPException
from typing import Sequence
from pathlib import Path

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core import ResumeVersion, Resume, User, Profile
from core.schemas.profile_schema import ProfileBase
from core.schemas.resume_schema import ResumeCreate, ResumeUpdate, ResumeBase
from core.schemas.resume_version_schema import ResumeVersionBase
from core.utils.agents.gpt_agent import ResumeServiceAgent
from core.utils.redis_cache import redis_cache


class ResumeService:

    @staticmethod
    async def create_resume_version(
            resume_data: ResumeCreate | ResumeUpdate,
            session: AsyncSession,
            resume_id: int,
            version: int = 1,
    ) -> ResumeVersion:
        async def create_version_object(resume_data, resume_id, version) -> ResumeVersion:
            version_data = ResumeVersionBase(
                **resume_data.model_dump(exclude={"version", "resume_id"}),
                version=version,
                resume_id=resume_id
            )
            return ResumeVersion(**version_data.model_dump(exclude_none=True))

        async def handle_profile_update(resume_data, session, resume_id, version_model) -> Profile:
            last_profile = await session.scalar(
                select(Profile)
                .where(ResumeVersion.resume_id == resume_id)
                .order_by(Profile.id.desc())
            )

            profile = ProfileBase(**resume_data.model_dump(exclude_none=True))

            if not last_profile:
                profile_model = Profile(**profile.model_dump(exclude_none=True), version_id=version_model.id)
                session.add(profile_model)
            else:
                profile_dict = {column.name: getattr(last_profile, column.name)
                                for column in Profile.__table__.columns}

                profile_data = {
                    key: profile.model_dump().get(key) if profile.model_dump().get(
                        key) is not None else profile_dict.get(
                        key)
                    for key in profile_dict.keys() | profile.model_dump().keys()
                }

                profile_data.pop("version_id")
                profile_data.pop("id")

                logger.info(f"Last profile: {profile_data}")
                profile_model = Profile(**profile_data, version_id=version_model.id)
                session.add(profile_model)

            await session.flush()
            return profile_model

        async def process_resume_service_call(resume_service, action, **kwargs) -> str:
            try:
                if action == "create_resume":
                    return await resume_service.create_resume(**kwargs)
                elif action == "edit_resume":
                    return await resume_service.edit_resume(**kwargs)
            except Exception as e:
                logger.error(f"Error in {action}: {e}")
                raise

        try:
            version_model = await create_version_object(resume_data, resume_id, version)
            session.add(version_model)
            await session.flush()

            profile_model = await handle_profile_update(resume_data, session, resume_id, version_model)

            path_to_instructions = os.path.join(Path(__file__).parent.parent, "utils/agents/agent_instructions")
            resume_service = ResumeServiceAgent(redis_client=redis_cache, instruction_dir=path_to_instructions)

            profile_dict = {column.name: getattr(profile_model, column.name)
                            for column in Profile.__table__.columns}

            profile_dict.pop("version_id")
            profile_dict.pop("id")

            logger.info(profile_dict)

            if isinstance(resume_data, ResumeCreate):
                version_model.path_to_html = await process_resume_service_call(
                    resume_service,
                    action="create_resume",
                    user_id=resume_data.user_id,
                    resume_id=resume_id,
                    input_resume=json.dumps(profile_dict)
                )
            elif isinstance(resume_data, ResumeUpdate):
                resume = await session.scalar(select(Resume).where(Resume.id == resume_id))
                version_model.path_to_html = await process_resume_service_call(
                    resume_service,
                    action="edit_resume",
                    user_id=resume.user_id,
                    instruction={"json": json.dumps(profile_dict), "prompt": resume_data.instructions},
                    version=resume.versions[-1].version,
                    resume_id=resume.id
                )

            await session.commit()

            await session.refresh(version_model)
            await session.refresh(profile_model)

            return version_model

        except Exception as e:
            logger.error(f"Error in create_resume_version: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def create(data: ResumeCreate, session: AsyncSession) -> Resume:
        user_exists = await session.scalar(select(User).where(User.telegram_id == data.user_id))

        if not user_exists:
            raise HTTPException(status_code=404, detail="User does not exist")

        resume = ResumeBase(**data.model_dump(exclude={"user_id"}))

        resume = Resume(**resume.model_dump(), user_id=data.user_id)
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

        update_data = data.model_dump(exclude_none=True)
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
