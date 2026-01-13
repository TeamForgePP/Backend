from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict

from src.core.db.enums import UserRole


class UserBase(BaseModel):
    last_name: str = Field(..., max_length=35)
    first_name: str = Field(..., max_length=20)
    patronymic: str | None = Field(default=None, max_length=35)
    email: EmailStr
    user_type: UserRole = UserRole.STUDENT
    avatar_url: str | None = Field(default=None)
    group_id: UUID | None = Field(default=None)
    in_team: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserProfileUpdate(BaseModel):
    last_name: str | None = Field(default=None, max_length=35)
    first_name: str | None = Field(default=None, max_length=20)
    patronymic: str | None = Field(default=None, max_length=35)
    email: EmailStr | None = None
    user_type: UserRole | None = None
    avatar_url: str | None = None
    group_id: UUID | None = None
    in_team: bool | None = None


class UserPasswordUpdate(BaseModel):
    email: EmailStr | None = None
    password: str = Field(default=..., min_length=6, max_length=128)


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
