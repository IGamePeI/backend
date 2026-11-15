from datetime import datetime

from pydantic import BaseModel

from .user import AuthorShort


class StepFeedbackCreate(BaseModel):
    step_id: int
    is_helpful: bool | None = None
    comment: str | None = None
    guest_name: str | None = None


class StepFeedback(BaseModel):
    id: int
    step_id: int
    user_id: int | None = None
    guest_name: str | None = None
    is_helpful: bool | None = None
    comment: str | None = None
    created_at: datetime
    user: AuthorShort | None = None

    class Config:
        from_attributes = True
