from datetime import datetime

from pydantic import BaseModel, EmailStr

from utils.enums import UserRole


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthorShort(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True
