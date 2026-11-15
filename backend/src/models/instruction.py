from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from .progress import UserProgress
    from .step import Step
    from .user import User


class Instruction(Base):
    __tablename__ = "instructions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("instructions.id", ondelete="SET NULL"), nullable=True)

    views_count: Mapped[int] = mapped_column(default=0, nullable=False)
    completions_count: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=text("TIMEZONE('utc', now())")
    )

    author: Mapped["User"] = relationship(back_populates="instructions")
    steps: Mapped[List["Step"]] = relationship(
        back_populates="instruction",
        cascade="all, delete-orphan",
        order_by="Step.step_number",
    )
    progress_records: Mapped[List["UserProgress"]] = relationship(
        back_populates="instruction", cascade="all, delete-orphan"
    )
    forks: Mapped[List["Instruction"]] = relationship("Instruction", remote_side=[id])  # noqa: A003
