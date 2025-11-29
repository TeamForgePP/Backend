from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import ProjectReports, Reports


class ReportsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Reports | None:
        result = await self._session.execute(select(Reports).where(Reports.id == id_))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Reports]:
        result = await self._session.execute(select(Reports))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> Reports:
        report = Reports(**data)
        self._session.add(report)
        await self._session.flush()
        await self._session.refresh(report)
        return report

    async def update(self, id_: UUID, data: dict[str, Any]) -> Reports | None:
        result = await self._session.execute(select(Reports).where(Reports.id == id_))
        report = result.scalar_one_or_none()
        if report is None:
            return None

        for field, value in data.items():
            setattr(report, field, value)

        await self._session.flush()
        await self._session.refresh(report)
        return report

    async def delete(self, id_: UUID) -> bool:
        result = await self._session.execute(select(Reports).where(Reports.id == id_))
        report = result.scalar_one_or_none()
        if report is None:
            return False

        await self._session.delete(report)
        await self._session.flush()
        return True

        # Доп. методы

    async def get_by_project(self, project_id: UUID) -> list[Reports]:
        result = await self._session.execute(
            select(Reports)
            .join(ProjectReports, ProjectReports.report_id == Reports.id)
            .where(ProjectReports.project_id == project_id)
        )
        return list(result.scalars().all())
