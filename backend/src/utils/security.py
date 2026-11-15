from datetime import timedelta
from typing import Any

import bcrypt
from authx import AuthX, AuthXConfig

from config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


config: AuthXConfig = AuthXConfig()
config.JWT_SECRET_KEY = settings.SECRET_KEY
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=15)
config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_ACCESS_COOKIE_NAME = settings.USER_ACCESS_TOKEN_NAME
config.JWT_REFRESH_COOKIE_NAME = settings.USER_REFRESH_TOKEN_NAME
config.JWT_TOKEN_LOCATION = ["cookies"]

security: AuthX[Any] = AuthX(config=config, model=None)
