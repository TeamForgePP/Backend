from pydantic import BaseModel, EmailStr


class ProfileResponse(BaseModel):
    full_name: str
    group: str | None
    role: str
    teams: list[str]
    email: EmailStr


class ProfileUpdateRequest(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None

    class Config:
        extra = "forbid"
