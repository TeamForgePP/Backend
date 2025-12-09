from typing import Any, cast
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Performes


class PerformesRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_by_task(self, task_id: UUID) -> list[Performes]:
        result = await self._session.execute(select(Performes).where(Performes.task_id == task_id))
        relations = result.scalars().all()
        return cast(list[Performes], relations)

    async def get_assignee_ids_by_task(self, task_id: UUID) -> list[UUID]:
        result = await self._session.execute(
            select(Performes.assigne_id).where(Performes.task_id == task_id)
        )
        ids = result.scalars().all()
        return cast(list[UUID], ids)

    async def add(self, task_id: UUID, assignee_id: UUID) -> Performes:
        data: dict[str, Any] = {
            "task_id": task_id,
            "assigne_id": assignee_id,
        }
        relation = Performes(**data)
        self._session.add(relation)
        await self._session.flush()
        await self._session.refresh(relation)
        return relation

    async def delete(self, task_id: UUID, assignee_id: UUID) -> bool:
        result = await self._session.execute(
            delete(Performes).where(
                Performes.task_id == task_id,
                Performes.assigne_id == assignee_id,
            )
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0
