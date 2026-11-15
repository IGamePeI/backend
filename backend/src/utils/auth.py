from fastapi import Depends, HTTPException, Request
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from crud import user as crud
from database.db import get_db_session
from models import user as user_model


def get_token(request: Request) -> str:
    token = request.cookies.get(settings.USER_ACCESS_TOKEN_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Токен не найден")
    return token


def get_refresh_token(request: Request) -> str:
    token = request.cookies.get(settings.USER_REFRESH_TOKEN_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Токен не найден")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")  # noqa: B904
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен не валидный")  # noqa: B904
    except Exception as e:
        print(f"[JWT Refresh Error] {e}")
        raise HTTPException(status_code=401, detail="Ошибка проверки токена")  # noqa: B904

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="ID пользователя не найден в токене")
    return str(user_id)


async def get_current_user(
    session: AsyncSession = Depends(get_db_session), token: str = Depends(get_token)
) -> user_model.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")  # noqa: B904
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен не валидный")  # noqa: B904
    except Exception as e:
        print(f"[JWT Access Error] {e}")
        raise HTTPException(status_code=401, detail="Ошибка проверки токена")  # noqa: B904

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="ID пользователя не найден в токене")

    user = await crud.get_user(session=session, user_id=int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


async def get_optional_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> user_model.User | None:
    token = request.cookies.get(settings.USER_ACCESS_TOKEN_NAME)
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return await crud.get_user(session=session, user_id=int(user_id))
    except Exception:
        return None
