from datetime import timedelta
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from crud import user as user_crud
from database.db import get_db_session
from schemas import user as schema
from utils import auth
from utils.modules.limiter import limiter
from utils.security import config, security, verify_password

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/login")
@limiter.limit("5/second")
async def login(
    request: Request, user: schema.UserLogin, response: Response, db: Annotated[AsyncSession, Depends(get_db_session)]
) -> Dict[str, str]:
    db_user = await user_crud.get_user_by_email(session=db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = security.create_access_token(uid=str(db_user.id), expiry=timedelta(seconds=20))
    refresh_token = security.create_refresh_token(uid=str(db_user.id), expiry=timedelta(days=7))

    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token, httponly=True, samesite="lax")
    response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, refresh_token, httponly=True, samesite="lax")
    response.set_cookie("is_login", "True", httponly=False, samesite="lax")
    return {"user_access_token": access_token}


@router.post("/refresh", dependencies=[Depends(security.refresh_token_required)])
async def refresh_access_token(
    request: Request, response: Response, user_id: Annotated[str, Depends(auth.get_refresh_token)]
) -> Dict[str, str]:
    new_access_token = security.create_access_token(uid=user_id, expiry=timedelta(seconds=20))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, new_access_token, httponly=True, secure=True, samesite="lax")
    return {"status": "refreshed"}


@router.get("/me", response_model=schema.User)
async def get_current_user(user_data: Annotated[schema.User, Depends(auth.get_current_user)]) -> schema.User:
    return user_data


@router.get("/logout")
@limiter.limit("5/second")
async def logout(request: Request, response: Response) -> Dict[str, str]:
    response.delete_cookie("is_login")
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(config.JWT_REFRESH_COOKIE_NAME)
    return {"status": "success"}
