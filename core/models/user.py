import datetime

from typing import List

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

class User(Base):
    __tablename__ = "tg_user"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # время ставит Postgres
        nullable=False
    )

    last_seen: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    resumes: Mapped[List["Resume"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (f""
                f"User(telegram_id={self.telegram_id!r}, "
                f"name={self.name!r}, "
                f"created_at={self.created_at!r}, "
                f"last_seen={self.last_seen!r})")