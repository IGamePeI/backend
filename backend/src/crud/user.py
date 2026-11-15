from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import user as user_model
from schemas import user as user_schema
from utils.security import get_password_hash


async def get_user(session: AsyncSession, user_id: int) -> user_model.User | None:
    result = await session.execute(select(user_model.User).filter(user_model.User.id == user_id))
    user = result.scalar_one_or_none()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> user_model.User | None:
    result = await session.execute(select(user_model.User).filter(user_model.User.email == email))
    user = result.scalar_one_or_none()
    return user


async def create_user(session: AsyncSession, user: user_schema.UserCreate) -> user_model.User:
    hashed_password = get_password_hash(user.password)
    db_user = user_model.User(username=user.username, email=user.email, password=hashed_password, role=user.role)
    session.add(db_user)
    await session.flush()
    await session.refresh(db_user)
    return db_user


async def update_user(session: AsyncSession, user_id: int, user: user_schema.UserUpdate) -> user_model.User | None:
    db_user = await get_user(session=session, user_id=user_id)
    if db_user:
        for key, value in user.model_dump(exclude_unset=True).items():
            if key != "password":
                setattr(db_user, key, value)
        session.add(db_user)
        await session.flush()
        await session.refresh(db_user)
        return db_user
    return None


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    db_user = await get_user(session=session, user_id=user_id)
    if db_user:
        await session.delete(db_user)
        await session.flush()
        return True
    return False
