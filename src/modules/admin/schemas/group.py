from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from src.core.db.enums import Faculty, LevelEducation


class GroupBase(BaseModel):
    name: str = Field(..., max_length=11)
    level_ed: LevelEducation
    faculty: Faculty
    year_adm: int
    curator_id: UUID | None = None
    students_count: int = 0


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=11)
    level_ed: LevelEducation | None = None
    faculty: Faculty | None = None
    year_adm: int | None = None
    curator_id: UUID | None = None


class GroupRead(GroupBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
