from typing import Any, cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import SprintStatus
from src.core.db.interfaces import BaseRepository
from src.core.db.models.sprints import Sprints


class SprintsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, sprint_id: UUID) -> Sprints | None:
        sprint = await self._session.get(Sprints, sprint_id)
        return cast(Sprints | None, sprint)

    async def get_next_seq_for_project(self, project_id: UUID) -> int:
        result = await self._session.execute(
            select(func.coalesce(func.max(Sprints.seq), 0)).where(Sprints.project_id == project_id)
        )
        max_seq = result.scalar_one()
        return int(max_seq) + 1

    async def get_by_project_id(
        self, project_id: UUID, status: SprintStatus | None = None
    ) -> list[Sprints]:
        stmt = select(Sprints).where(Sprints.project_id == project_id).order_by(Sprints.seq)

        if status is not None:
            stmt = stmt.where(Sprints.status == status)

        sprints = (await self._session.execute(stmt)).scalars().all()
        return cast(list[Sprints], sprints)

    async def get_future_sprints_in_project(self, project_id: UUID) -> list[Sprints]:
        result = await self._session.execute(
            select(Sprints)
            .where(
                Sprints.project_id == project_id,
                Sprints.status == SprintStatus.UPCOMING,
            )
            .order_by(Sprints.seq)
        )
        sprints = result.scalars().all()
        return cast(list[Sprints], sprints)

    async def get_active_sprint_in_project(self, project_id: UUID) -> Sprints | None:
        result = await self._session.execute(
            select(Sprints).where(
                Sprints.project_id == project_id,
                Sprints.status == SprintStatus.ACTIVE,
            )
        )
        sprint = result.scalar_one_or_none()
        return cast(Sprints | None, sprint)

    async def get_all(self) -> list[Sprints]:
        result = await self._session.execute(select(Sprints))
        sprints = result.scalars().all()
        return cast(list[Sprints], sprints)

    async def create(self, data: dict[str, Any]) -> Sprints:
        sprint = Sprints(**data)
        self._session.add(sprint)
        await self._session.flush()
        await self._session.refresh(sprint)
        return sprint

    async def update(self, sprint_id: UUID, data: dict[str, Any]) -> Sprints | None:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return None

        for field, value in data.items():
            setattr(sprint, field, value)

        await self._session.flush()
        await self._session.refresh(sprint)
        return sprint

    async def delete(self, sprint_id: UUID) -> bool:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return False

        await self._session.delete(sprint)
        await self._session.flush()
        return True
