from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.entity.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=10)
    phone_number: str = Field(min_length=6, max_length=20)
    


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    phone_number: str
    created_at: datetime
    role: Role
    telegram_token: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    phone_number: str | None = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    username: str
    email: EmailStr
    phone_number: str
    created_at: datetime


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class UserTelegram(BaseModel):
    email: str
    chat_id: str
