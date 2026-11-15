from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from crud import instruction as instruction_crud
from crud import step as step_crud
from database.db import get_db_session
from models import user as user_model
from schemas import step as step_schema
from utils.auth import get_current_user
from utils.modules.limiter import limiter
from utils.modules.redis import get_redis

router = APIRouter(prefix="/v1/steps", tags=["Steps"])


@router.post("/instruction/{instruction_id}", response_model=step_schema.Step, status_code=201)
@limiter.limit("5/second")
async def add_step(
    request: Request,
    instruction_id: int,
    step: step_schema.StepCreate,
    current_user: Annotated[user_model.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> Any:
    instruction = await instruction_crud.get_instruction(session=db, instruction_id=instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Instruction not found")
    if instruction.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    new_step = await step_crud.create_step(session=db, instruction_id=instruction_id, data=step)
    await redis.delete(f"instruction:{instruction_id}")
    return new_step


@router.patch("/{step_id}", response_model=step_schema.Step)
@limiter.limit("5/second")
async def update_step(
    request: Request,
    step_id: int,
    step: step_schema.StepUpdate,
    current_user: Annotated[user_model.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> Any:
    db_step = await step_crud.get_step(session=db, step_id=step_id)
    if db_step is None:
        raise HTTPException(status_code=404, detail="Step not found")

    instruction = await instruction_crud.get_instruction(session=db, instruction_id=db_step.instruction_id)
    if not instruction or instruction.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_step = await step_crud.update_step(session=db, step_id=step_id, data=step)
    await redis.delete(f"instruction:{db_step.instruction_id}")
    return updated_step


@router.delete("/{step_id}", status_code=204)
@limiter.limit("5/second")
async def delete_step(
    request: Request,
    step_id: int,
    current_user: Annotated[user_model.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> None:
    db_step = await step_crud.get_step(session=db, step_id=step_id)
    if db_step is None:
        raise HTTPException(status_code=404, detail="Step not found")

    instruction = await instruction_crud.get_instruction(session=db, instruction_id=db_step.instruction_id)
    if not instruction or instruction.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    instruction_id = db_step.instruction_id
    await step_crud.delete_step(session=db, step_id=step_id)
    await redis.delete(f"instruction:{instruction_id}")
    return None
