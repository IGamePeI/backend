from datetime import datetime

from pydantic import BaseModel

from .step import Step, StepCreate
from .user import AuthorShort


class InstructionCreate(BaseModel):
    title: str
    description: str
    category: str
    tags: str | None = None
    steps: list[StepCreate]


class InstructionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    tags: str | None = None


class InstructionShort(BaseModel):
    id: int
    title: str
    description: str
    category: str
    tags: str | None = None
    parent_id: int | None = None
    views_count: int
    completions_count: int
    created_at: datetime
    author: AuthorShort

    class Config:
        from_attributes = True


class Instruction(InstructionShort):
    updated_at: datetime
    steps: list[Step]
