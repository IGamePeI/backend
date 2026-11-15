from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import feedback as feedback_model
from models import progress as progress_model
from models import step as step_model
from schemas import progress as progress_schema


async def upsert_progress(
    session: AsyncSession,
    data: progress_schema.ProgressUpdate,
    user_id: int | None = None,
) -> progress_model.UserProgress:
    query = select(progress_model.UserProgress).filter(
        progress_model.UserProgress.instruction_id == data.instruction_id
    )

    if user_id:
        query = query.filter(progress_model.UserProgress.user_id == user_id)
    else:
        query = query.filter(progress_model.UserProgress.session_id == data.session_id)

    result = await session.execute(query)
    db_progress = result.scalar_one_or_none()

    if db_progress:
        was_completed = db_progress.is_completed
        db_progress.last_completed_step = max(db_progress.last_completed_step, data.last_completed_step)
        db_progress.is_completed = data.is_completed or was_completed
    else:
        db_progress = progress_model.UserProgress(
            user_id=user_id,
            session_id=None if user_id else data.session_id,
            instruction_id=data.instruction_id,
            last_completed_step=data.last_completed_step,
            is_completed=data.is_completed,
        )
        session.add(db_progress)

    await session.flush()
    await session.refresh(db_progress)
    return db_progress


async def get_instruction_analytics(
    session: AsyncSession, instruction_id: int
) -> progress_schema.InstructionAnalytics | None:
    steps_res = await session.execute(
        select(step_model.Step)
        .filter(step_model.Step.instruction_id == instruction_id)
        .order_by(step_model.Step.step_number)
    )
    steps = list(steps_res.scalars().all())
    if not steps:
        return None
    prog_res = await session.execute(
        select(progress_model.UserProgress).filter(progress_model.UserProgress.instruction_id == instruction_id)
    )
    progress_list = list(prog_res.scalars().all())

    total_started = len(progress_list)
    total_completed = sum(1 for p in progress_list if p.is_completed)
    completion_rate = round((total_completed / total_started * 100), 1) if total_started > 0 else 0.0

    steps_stats: list[progress_schema.StepBottleneckStat] = []

    for step in steps:
        reached = sum(1 for p in progress_list if p.last_completed_step >= step.step_number - 1)
        dropped = sum(1 for p in progress_list if not p.is_completed and p.last_completed_step == step.step_number - 1)

        dislikes_res = await session.execute(
            select(func.count(feedback_model.StepFeedback.id)).filter(
                feedback_model.StepFeedback.step_id == step.id,
                feedback_model.StepFeedback.is_helpful.is_(False),
            )
        )
        dislikes_count = dislikes_res.scalar() or 0

        steps_stats.append(
            progress_schema.StepBottleneckStat(
                step_number=step.step_number,
                step_title=step.title,
                users_reached=reached,
                users_dropped_here=dropped,
                dislikes_count=dislikes_count,
            )
        )

    return progress_schema.InstructionAnalytics(
        instruction_id=instruction_id,
        total_started=total_started,
        total_completed=total_completed,
        completion_rate=completion_rate,
        steps_stats=steps_stats,
    )
