import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from crud import instruction as instruction_crud
from database.db import get_db_session
from models import user as user_model
from schemas import instruction as instruction_schema
from utils.auth import get_current_user
from utils.modules.limiter import limiter
from utils.modules.redis import get_redis

router = APIRouter(prefix="/v1/instructions", tags=["Instructions"])

class InstructionCatalogItem(instruction_schema.InstructionShort):
    steps_count: int = 0

@router.get("/", response_model=list[InstructionCatalogItem])
@limiter.limit("10/second")
async def read_instructions(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    category: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    return await instruction_crud.get_instructions(session=db, category=category, search=search, skip=skip, limit=limit)


@router.post("/", response_model=instruction_schema.Instruction, status_code=201)
@limiter.limit("5/second")
async def create_instruction(
    request: Request,
    instruction: instruction_schema.InstructionCreate,
    current_user: Annotated[user_model.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Any:
    return await instruction_crud.create_instruction(session=db, author_id=current_user.id, data=instruction)


@router.get("/{instruction_id}", response_model=instruction_schema.Instruction)
@limiter.limit("10/second")
async def read_instruction(
    request: Request,
    instruction_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> Any:
    cache_key = f"instruction:{instruction_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    db_instruction = await instruction_crud.get_instruction(session=db, instruction_id=instruction_id)
    if db_instruction is None:
        raise HTTPException(status_code=404, detail="Instruction not found")

    db_instruction.views_count += 1
    await db.flush()
    await db.refresh(db_instruction)

    data = instruction_schema.Instruction.model_validate(db_instruction).model_dump(mode="json")
    await redis.setex(cache_key, 300, json.dumps(data))
    return db_instruction


@router.post("/{instruction_id}/fork", response_model=instruction_schema.Instruction, status_code=201)
@limiter.limit("3/second")
async def fork_instruction(
    request: Request,
    instruction_id: int,
    current_user: Annotated[user_model.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Any:
    forked = await instruction_crud.fork_instruction(
        session=db, original_id=instruction_id, new_author_id=current_user.id
    )
    if forked is None:
        raise HTTPException(status_code=404, detail="Original instruction not found")
    return forked


@router.delete("/{instruction_id}", status_code=204)
@limiter.limit("5/second")
async def delete_instruction(
    request: Request,
    instruction_id: int,
    current_user: Annotated[user_model.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> None:
    db_instruction = await instruction_crud.get_instruction(session=db, instruction_id=instruction_id)
    if db_instruction is None:
        raise HTTPException(status_code=404, detail="Instruction not found")
    if db_instruction.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await instruction_crud.delete_instruction(session=db, instruction_id=instruction_id)
    await redis.delete(f"instruction:{instruction_id}")
    return None
