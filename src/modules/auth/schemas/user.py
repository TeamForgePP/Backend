from typing import Literal

from pydantic import BaseModel, EmailStr


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserTokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
