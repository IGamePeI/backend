from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from .step import Step
    from .user import User


class StepFeedback(Base):
    __tablename__ = "step_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    step_id: Mapped[int] = mapped_column(ForeignKey("steps.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    guest_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    is_helpful: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    step: Mapped["Step"] = relationship(back_populates="feedbacks")
    user: Mapped[Optional["User"]] = relationship(back_populates="feedbacks")
