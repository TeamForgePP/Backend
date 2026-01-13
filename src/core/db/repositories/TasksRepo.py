from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.enums import TaskStatus
from src.core.db.interfaces import BaseRepository
from src.core.db.models.tasks import Tasks


class TasksRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, task_id: UUID) -> Tasks | None:
        task = await self._session.get(Tasks, task_id)
        return cast(Tasks | None, task)

    async def get_all(self) -> list[Tasks]:
        result = await self._session.execute(select(Tasks))
        tasks = result.scalars().all()
        return cast(list[Tasks], tasks)

    async def get_by_project(
        self,
        project_id: UUID,
        status: TaskStatus | None = None,
    ) -> list[Tasks]:
        stmt = select(Tasks).where(Tasks.project_id == project_id).order_by(Tasks.seq)

        if status is not None:
            stmt = stmt.where(Tasks.status == status)

        result = await self._session.execute(stmt)
        tasks = result.scalars().all()
        return cast(list[Tasks], tasks)

    async def get_by_sprint_id(self, sprint_id: UUID) -> list[Tasks]:
        result = (
            (
                await self._session.execute(
                    select(Tasks).where(Tasks.sprint_id == sprint_id).order_by(Tasks.seq)
                )
            )
            .scalars()
            .all()
        )
        return cast(list[Tasks], result)

    async def create(self, data: dict[str, Any]) -> Tasks:
        task = Tasks(**data)
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def update(self, task_id: UUID, data: dict[str, Any]) -> Tasks | None:
        task = await self.get_by_id(task_id)
        if task is None:
            return None

        for field, value in data.items():
            setattr(task, field, value)

        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def delete(self, task_id: UUID) -> bool:
        task = await self.get_by_id(task_id)
        if task is None:
            return False

        await self._session.delete(task)
        await self._session.flush()
        return True
