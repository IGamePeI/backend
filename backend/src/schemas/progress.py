from datetime import datetime

from pydantic import BaseModel


class ProgressUpdate(BaseModel):
    instruction_id: int
    last_completed_step: int
    is_completed: bool = False
    session_id: str | None = None


class UserProgress(BaseModel):
    id: int
    user_id: int | None = None
    session_id: str | None = None
    instruction_id: int
    last_completed_step: int
    is_completed: bool
    started_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StepBottleneckStat(BaseModel):
    step_number: int
    step_title: str
    users_reached: int
    users_dropped_here: int
    dislikes_count: int


class InstructionAnalytics(BaseModel):
    instruction_id: int
    total_started: int
    total_completed: int
    completion_rate: float
    steps_stats: list[StepBottleneckStat]
