from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from crud import feedback as feedback_crud
from crud import step as step_crud
from database.db import get_db_session
from models import user as user_model
from schemas import feedback as feedback_schema
from utils.auth import get_optional_user
from utils.modules.limiter import limiter

router = APIRouter(prefix="/v1/feedbacks", tags=["Step Feedbacks"])


@router.post("/", response_model=feedback_schema.StepFeedback, status_code=201)
@limiter.limit("5/second")
async def create_step_feedback(
    request: Request,
    feedback: feedback_schema.StepFeedbackCreate,
    current_user: Annotated[user_model.User | None, Depends(get_optional_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Any:
    step = await step_crud.get_step(session=db, step_id=feedback.step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    user_id = current_user.id if current_user else None
    return await feedback_crud.create_feedback(session=db, data=feedback, user_id=user_id)


@router.get("/step/{step_id}", response_model=list[feedback_schema.StepFeedback])
@limiter.limit("10/second")
async def read_step_feedbacks(
    request: Request,
    step_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Any:
    return await feedback_crud.get_step_feedbacks(session=db, step_id=step_id)
