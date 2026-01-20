from uuid import UUID

from pydantic import BaseModel, EmailStr


class ProfileResponse(BaseModel):
    full_name: str
    group: str | None
    role: str | None
    active_project: str | None
    email: EmailStr


class ProfileUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    group_id: UUID | None = None
