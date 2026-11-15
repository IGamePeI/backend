import json
from typing import Annotated, Any, Sequence

from fastapi import APIRouter, Depends, HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from crud import user as user_crud
from database.db import get_db_session
from models import user as user_model
from schemas import user as user_schema
from utils.modules.limiter import limiter
from utils.modules.redis import get_redis

router = APIRouter(prefix="/v1/users", tags=["Users"])


@router.post("/", response_model=user_schema.User, status_code=201)
@limiter.limit("5/second")
async def create_user(
    request: Request, user: user_schema.UserCreate, db: Annotated[AsyncSession, Depends(get_db_session)]
) -> Sequence[user_model.User] | Any:
    db_user = await user_crud.get_user_by_email(session=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_crud.create_user(session=db, user=user)


@router.get("/{user_id}", response_model=user_schema.User)
@limiter.limit("5/second")
async def read_user(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> Sequence[user_model.User] | Any:
    cache_key = f"user:{user_id}"
    cached_user = await redis.get(cache_key)
    if cached_user:
        return json.loads(cached_user)
    db_user = await user_crud.get_user(session=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_schema.User.model_validate(db_user).model_dump(mode="json")
    await redis.setex(cache_key, 600, json.dumps(user_data))
    return db_user


@router.patch("/{user_id}", response_model=user_schema.User)
@limiter.limit("5/second")
async def update_user(
    request: Request,
    user_id: int,
    user: user_schema.UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> Sequence[user_model.User] | Any:
    updated_user = await user_crud.update_user(session=db, user_id=user_id, user=user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await db.refresh(updated_user)
    await redis.delete(f"user:{user_id}")
    return updated_user


@router.delete("/{user_id}", status_code=204)
@limiter.limit("5/second")
async def delete_user(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> None:
    deleted = await user_crud.delete_user(session=db, user_id=user_id)
    if deleted:
        await redis.delete(f"user:{user_id}")
        return None
    else:
        raise HTTPException(status_code=404, detail="User not found")
