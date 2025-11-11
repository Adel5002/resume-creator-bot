from fastapi import APIRouter

from core.schemas.resume_schema import ResumeRead, ResumeCreate, ResumeUpdate
from core.db.db import SessionDep
from core.services.resume_service import ResumeService

router = APIRouter()


@router.post("/create/", response_model=ResumeRead)
async def create_resume(data: ResumeCreate, session: SessionDep):
    return await ResumeService.create(data=data, session=session)

@router.get("/user/{user_id}/", response_model=list[ResumeRead])
async def list_user_resumes(user_id: int, session: SessionDep):
    return await ResumeService.list_by_user(user_id=user_id, session=session)

@router.get("/get/{resume_id}/", response_model=ResumeRead)
async def get_resume(resume_id: int, session: SessionDep):
    return await ResumeService.get_by_id(resume_id=resume_id, session=session)

@router.patch("/update/{resume_id}/", response_model=ResumeRead)
async def update_resume(resume_id: int, data: ResumeUpdate, session: SessionDep):
    return await ResumeService.update(resume_id=resume_id, data=data, session=session)

@router.delete("/delete/{resume_id}/")
async def delete_resume(resume_id: int, session: SessionDep):
    await ResumeService.delete(resume_id=resume_id, session=session)
    return {"detail": "Resume deleted"}
