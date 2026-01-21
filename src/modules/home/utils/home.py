from collections.abc import Iterable
from datetime import date, datetime
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import (
    TeamRole,
    UnitOfWork,
    UserStatus,
)
from src.modules.home.schemas import User, UsersResponse


class HomeUtils:
    @classmethod
    async def mark_all_team(cls, uow: UnitOfWork, project_id: UUID) -> None:
        team_rows = await uow.teams.get_by_project(project_id=project_id)
        team_rows = team_rows or []

        for team in team_rows:
            if getattr(team, "status", None) not in (UserStatus.Owner, UserStatus.Member):
                continue

            member_id = getattr(team, "user_id", None)
            if isinstance(member_id, UUID):
                await uow.users.mark_in_team(user_id=member_id, bool_team=False)

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

    @staticmethod
    def to_users_response(users: Iterable[object] | None) -> UsersResponse:
        if not users:
            return UsersResponse(users=[])

        result: list[User] = []

        for u in users:
            uid = getattr(u, "id", None)
            if not isinstance(uid, UUID):
                continue

            result.append(
                User(
                    id=uid,
                    name=HomeUtils.as_str(getattr(u, "first_name", "")),
                    last_name=HomeUtils.as_str(getattr(u, "last_name", "")),
                    in_team=HomeUtils.as_bool(getattr(u, "in_team", False)),
                )
            )

        return UsersResponse(users=result)

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
