from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import Teams, Users


class UsersRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, user_id: UUID) -> Users | None:
        user = await self._session.get(Users, user_id)
        return cast(Users | None, user)

    async def get_by_group(self, group_id: UUID) -> list[Users]:
        result = await self._session.execute(select(Users).where(Users.group_id == group_id))
        return cast(list[Users], result.scalars().all())

    async def get_by_email(self, email: str) -> Users | None:
        result = await self._session.execute(select(Users).where(Users.email == email))
        return cast(Users | None, result.scalar_one_or_none())

    async def get_by_project_id(self, project_id: UUID) -> list[Users]:
        users_id = (
            (
                await self._session.execute(
                    select(Teams.user_id).where(Teams.project_id == project_id)
                )
            )
            .scalars()
            .all()
        )
        if not users_id:
            return []
        result = (
            (await self._session.execute(select(Users).where(Users.id.in_(users_id))))
            .scalars()
            .all()
        )

        return cast(list[Users], result)

    async def get_all(self) -> list[Users]:
        result = await self._session.execute(select(Users))
        return cast(list[Users], result.scalars().all())

    async def mark_in_team(self, user_id: UUID, bool_team: bool) -> Users | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        user.in_team = bool_team

        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def create(self, data: dict[str, Any]) -> Users:
        user = Users(**data)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(self, user_id: UUID, data: dict[str, Any]) -> Users | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        for field, value in data.items():
            setattr(user, field, value)

        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        await self._session.delete(user)
        await self._session.flush()
        return True
