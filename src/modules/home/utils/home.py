from datetime import date, datetime
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import TeamRole


class HomeUtils:
    @classmethod
    def parse_uuid(cls, value: str, *, detail: str) -> UUID:
        try:
            return UUID(value)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail) from e

    @classmethod
    def as_team_role(cls, role: object) -> TeamRole:
        if isinstance(role, TeamRole):
            return role
        if isinstance(role, str):
            role_str: str = role
            try:
                return TeamRole(role_str)
            except Exception:
                by_name = TeamRole.__members__.get(role_str)
                if by_name is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="Invalid team role format",
                    ) from None
                return by_name

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid team role format",
        )

    @classmethod
    def is_active_sprint(cls, status_value: object) -> bool:
        if status_value is None:
            return False
        if isinstance(status_value, str):
            return status_value.strip().lower() == "active"
        v = getattr(status_value, "value", None)
        if isinstance(v, str) and v.strip().lower() == "active":
            return True
        n = getattr(status_value, "name", None)
        if isinstance(n, str) and n.strip().lower() == "active":
            return True
        return False

    @classmethod
    def safe_deadline_list(cls, values: list[object]) -> list[datetime]:
        out: list[datetime] = []
        for v in values:
            if isinstance(v, datetime):
                out.append(v)
        return out

    @classmethod
    def as_date(cls, value: object) -> date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        return date.min

    @classmethod
    def as_str(cls, value: object) -> str:
        if isinstance(value, str):
            return value
        return str(value)

    @classmethod
    def as_bool(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        return bool(value)
