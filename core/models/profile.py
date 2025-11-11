from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, JSON, ForeignKey
from core.models.base import Base


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    position: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    contacts: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    skills: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=None)
    experience: Mapped[list[dict]] = mapped_column(JSON, nullable=True, default=None)
    education: Mapped[list[dict]] = mapped_column(JSON, nullable=True, default=None)

    version_id: Mapped[int] = mapped_column(ForeignKey("resume_version.id", ondelete="CASCADE"))
    version: Mapped["ResumeVersion"] = relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"Profile(name={self.name!r}, position={self.position!r}, version_id={self.version_id!r})"
