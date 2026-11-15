from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from .feedback import StepFeedback
    from .instruction import Instruction


class Step(Base):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    instruction_id: Mapped[int] = mapped_column(ForeignKey("instructions.id", ondelete="CASCADE"), nullable=False)
    step_number: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=text("TIMEZONE('utc', now())")
    )

    instruction: Mapped["Instruction"] = relationship(back_populates="steps")
    feedbacks: Mapped[List["StepFeedback"]] = relationship(back_populates="step", cascade="all, delete-orphan")
