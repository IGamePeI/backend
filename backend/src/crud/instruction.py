from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import instruction as instruction_model
from models import step as step_model
from schemas import instruction as instruction_schema


async def get_instructions(
    session: AsyncSession,
    category: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[instruction_model.Instruction]:
    query = select(instruction_model.Instruction).options(selectinload(instruction_model.Instruction.author))

    if category:
        query = query.filter(instruction_model.Instruction.category == category)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                instruction_model.Instruction.title.ilike(pattern),
                instruction_model.Instruction.description.ilike(pattern),
                instruction_model.Instruction.tags.ilike(pattern),
            )
        )

    query = query.order_by(instruction_model.Instruction.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_instruction(session: AsyncSession, instruction_id: int) -> instruction_model.Instruction | None:
    query = (
        select(instruction_model.Instruction)
        .options(
            selectinload(instruction_model.Instruction.author),
            selectinload(instruction_model.Instruction.steps),
        )
        .filter(instruction_model.Instruction.id == instruction_id)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_instruction(
    session: AsyncSession,
    author_id: int,
    data: instruction_schema.InstructionCreate,
    parent_id: int | None = None,
) -> instruction_model.Instruction:
    db_instruction = instruction_model.Instruction(
        title=data.title,
        description=data.description,
        category=data.category,
        tags=data.tags,
        author_id=author_id,
        parent_id=parent_id,
    )
    session.add(db_instruction)
    await session.flush()

    for step_data in data.steps:
        db_step = step_model.Step(
            instruction_id=db_instruction.id,
            step_number=step_data.step_number,
            title=step_data.title,
            content=step_data.content,
            image_url=step_data.image_url,
        )
        session.add(db_step)
    await session.flush()
    created_instruction = await get_instruction(session, db_instruction.id)
    assert created_instruction is not None
    await session.refresh(db_step)
    return created_instruction


async def fork_instruction(
    session: AsyncSession, original_id: int, new_author_id: int
) -> instruction_model.Instruction | None:
    original = await get_instruction(session, original_id)
    if not original:
        return None

    fork_data = instruction_schema.InstructionCreate(
        title=f"{original.title} (улучшенная версия)",
        description=original.description,
        category=original.category,
        tags=original.tags,
        steps=[
            instruction_schema.StepCreate(
                step_number=s.step_number,
                title=s.title,
                content=s.content,
                image_url=s.image_url,
            )
            for s in original.steps
        ],
    )
    return await create_instruction(
        session=session,
        author_id=new_author_id,
        data=fork_data,
        parent_id=original.id,
    )


async def delete_instruction(session: AsyncSession, instruction_id: int) -> bool:
    db_instruction = await get_instruction(session, instruction_id)
    if db_instruction:
        await session.delete(db_instruction)
        await session.flush()
        return True
    return False
