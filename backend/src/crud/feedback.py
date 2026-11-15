from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import feedback as feedback_model
from schemas import feedback as feedback_schema


async def create_feedback(
    session: AsyncSession,
    data: feedback_schema.StepFeedbackCreate,
    user_id: int | None = None,
) -> feedback_model.StepFeedback:
    db_feedback = feedback_model.StepFeedback(
        step_id=data.step_id,
        user_id=user_id,
        guest_name=None if user_id else (data.guest_name or "Гость"),
        is_helpful=data.is_helpful,
        comment=data.comment,
    )
    session.add(db_feedback)
    await session.flush()
    await session.refresh(db_feedback)
    return db_feedback


async def get_step_feedbacks(session: AsyncSession, step_id: int) -> list[feedback_model.StepFeedback]:
    query = (
        select(feedback_model.StepFeedback)
        .options(selectinload(feedback_model.StepFeedback.user))
        .filter(feedback_model.StepFeedback.step_id == step_id)
        .order_by(feedback_model.StepFeedback.created_at.desc())
    )
    result = await session.execute(query)
    return list(result.scalars().all())
