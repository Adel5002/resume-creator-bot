from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func, Enum as SqlEnum

from typing import List

from core.models.base import Base
from enum import Enum

class ResumeCreationMode(str, Enum):
    NEW = "new"
    IMPORTED = "imported"
    TEMPLATE = "template"

class Resume(Base):
    __tablename__ = "resume"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

    creation_mode: Mapped[ResumeCreationMode] = mapped_column(
        SqlEnum(ResumeCreationMode),
        default=ResumeCreationMode.NEW,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("tg_user.telegram_id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="resumes")

    versions: Mapped[List["ResumeVersion"]] = relationship(
        back_populates="resume",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (f""
                f"Resume(id={self.id!r}, "
                f"title={self.title!r}, "
                f"creation_mode={self.creation_mode!r}, "
                f"created_at={self.created_at!r}, "
                f"user_id={self.user_id!r})")