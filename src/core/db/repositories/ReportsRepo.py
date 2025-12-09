from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import ProjectReports, Reports


class ReportsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, report_id: UUID) -> Reports | None:
        report = await self._session.get(Reports, report_id)
        return cast(Reports | None, report)

    async def get_all(self) -> list[Reports]:
        result = await self._session.execute(select(Reports))
        reports = result.scalars().all()
        return cast(list[Reports], reports)

    async def create(self, data: dict[str, Any]) -> Reports:
        report = Reports(**data)
        self._session.add(report)
        await self._session.flush()
        await self._session.refresh(report)
        return report

    async def update(self, report_id: UUID, data: dict[str, Any]) -> Reports | None:
        report = await self.get_by_id(report_id)
        if report is None:
            return None

        for field, value in data.items():
            setattr(report, field, value)

        await self._session.flush()
        await self._session.refresh(report)
        return report

    async def delete(self, report_id: UUID) -> bool:
        report = await self.get_by_id(report_id)
        if report is None:
            return False

        await self._session.delete(report)
        await self._session.flush()
        return True

    async def get_by_project(self, project_id: UUID) -> list[Reports]:
        result = await self._session.execute(
            select(Reports)
            .join(ProjectReports, ProjectReports.report_id == Reports.id)
            .where(ProjectReports.project_id == project_id)
        )
        reports = result.scalars().all()
        return cast(list[Reports], reports)
