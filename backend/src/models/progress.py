from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from .instruction import Instruction
    from .user import User


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "instruction_id", name="uq_user_instruction_progress"),
        UniqueConstraint("session_id", "instruction_id", name="uq_session_instruction_progress"),
        CheckConstraint("user_id IS NOT NULL OR session_id IS NOT NULL", name="chk_user_or_session"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    instruction_id: Mapped[int] = mapped_column(ForeignKey("instructions.id", ondelete="CASCADE"), nullable=False)

    last_completed_step: Mapped[int] = mapped_column(default=0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    started_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=text("TIMEZONE('utc', now())")
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="progress_records")
    instruction: Mapped["Instruction"] = relationship(back_populates="progress_records")
