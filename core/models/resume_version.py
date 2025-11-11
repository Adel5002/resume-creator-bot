from datetime import datetime

from sqlalchemy import JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base


class ResumeVersion(Base):
    __tablename__ = "resume_version"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int]
    extra_info_json: Mapped[dict | None] = mapped_column(JSON, default=None)
    path_to_html: Mapped[str | None] = mapped_column(default=None)
    path_to_image: Mapped[str | None] = mapped_column(default=None)
    path_to_pdf: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    resume_id: Mapped[int] = mapped_column(ForeignKey("resume.id", ondelete="CASCADE"))
    resume: Mapped["Resume"] = relationship(back_populates="versions")

    profile: Mapped["Profile"] = relationship(back_populates="version", lazy="selectin")

    def __repr__(self) -> str:
        return (f""
                f"ResumeVersion(id={self.id!r}, "
                f"version={self.version!r}, "
                f"profile_json={self.extra_info_json!r}, "
                f"path_to_html={self.path_to_html!r}, "
                f"path_to_image={self.path_to_image!r}, "
                f"path_to_pdf={self.path_to_pdf!r}, "
                f"created_at={self.created_at!r}, "
                f"resume_id={self.resume_id!r})")
