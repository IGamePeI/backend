from datetime import datetime

from pydantic import BaseModel


class StepCreate(BaseModel):
    step_number: int
    title: str
    content: str
    image_url: str | None = None


class StepUpdate(BaseModel):
    step_number: int | None = None
    title: str | None = None
    content: str | None = None
    image_url: str | None = None


class Step(BaseModel):
    id: int
    instruction_id: int
    step_number: int
    title: str
    content: str
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
