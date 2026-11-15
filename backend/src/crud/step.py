from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import step as step_model
from schemas import step as step_schema


async def get_step(session: AsyncSession, step_id: int) -> step_model.Step | None:
    result = await session.execute(select(step_model.Step).filter(step_model.Step.id == step_id))
    return result.scalar_one_or_none()


async def create_step(session: AsyncSession, instruction_id: int, data: step_schema.StepCreate) -> step_model.Step:
    db_step = step_model.Step(
        instruction_id=instruction_id,
        step_number=data.step_number,
        title=data.title,
        content=data.content,
        image_url=data.image_url,
    )
    session.add(db_step)
    await session.flush()
    await reorder_steps(session, instruction_id)
    await session.refresh(db_step)
    return db_step


async def update_step(session: AsyncSession, step_id: int, data: step_schema.StepUpdate) -> step_model.Step | None:
    db_step = await get_step(session, step_id)
    if not db_step:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_step, key, value)

    session.add(db_step)
    await session.flush()

    if data.step_number is not None:
        await reorder_steps(session, db_step.instruction_id)
    await session.refresh(db_step)
    return db_step


async def delete_step(session: AsyncSession, step_id: int) -> bool:
    db_step = await get_step(session, step_id)
    if not db_step:
        return False

    instruction_id = db_step.instruction_id
    await session.delete(db_step)
    await session.flush()

    await reorder_steps(session, instruction_id)
    await session.refresh(db_step)
    return True


async def reorder_steps(session: AsyncSession, instruction_id: int) -> None:
    result = await session.execute(
        select(step_model.Step)
        .filter(step_model.Step.instruction_id == instruction_id)
        .order_by(step_model.Step.step_number, step_model.Step.id)
    )
    steps = list(result.scalars().all())
    for index, step in enumerate(steps, start=1):
        step.step_number = index
    await session.flush()
