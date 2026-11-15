from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from crud import instruction as instruction_crud
from crud import progress as progress_crud
from database.db import get_db_session
from models import user as user_model
from schemas import progress as progress_schema
from utils.auth import get_optional_user
from utils.modules.limiter import limiter

router = APIRouter(prefix="/v1/progress", tags=["Progress & Analytics"])


@router.post("/", response_model=progress_schema.UserProgress)
@limiter.limit("15/second")
async def update_user_progress(
    request: Request,
    data: progress_schema.ProgressUpdate,
    current_user: Annotated[user_model.User | None, Depends(get_optional_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Any:
    user_id = current_user.id if current_user else None

    if user_id is None and not data.session_id:
        raise HTTPException(status_code=400, detail="Either authenticated user or session_id is required")

    instruction = await instruction_crud.get_instruction(session=db, instruction_id=data.instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Instruction not found")

    progress = await progress_crud.upsert_progress(session=db, data=data, user_id=user_id)

    if data.is_completed:
        instruction.completions_count += 1
        await db.flush()

    return progress


@router.get("/analytics/{instruction_id}", response_model=progress_schema.InstructionAnalytics)
@limiter.limit("5/second")
async def get_instruction_analytics(
    request: Request,
    instruction_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Any:
    analytics = await progress_crud.get_instruction_analytics(session=db, instruction_id=instruction_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Instruction or steps not found")
    return analytics
