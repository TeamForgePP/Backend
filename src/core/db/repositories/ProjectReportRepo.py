from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import ProjectReports


class ProjectReportsRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_by_project(self, project_id: UUID) -> list[ProjectReports]:
        result = await self._session.execute(
            select(ProjectReports).where(ProjectReports.project_id == project_id)
        )
        relations = result.scalars().all()
        return cast(list[ProjectReports], relations)

    async def get_report_ids_by_project(self, project_id: UUID) -> list[UUID]:
        result = await self._session.execute(
            select(ProjectReports.report_id).where(ProjectReports.project_id == project_id)
        )
        ids = result.scalars().all()
        return cast(list[UUID], ids)

    async def add_link(self, project_id: UUID, report_id: UUID) -> ProjectReports:
        data: dict[str, Any] = {
            "project_id": project_id,
            "report_id": report_id,
        }
        relation = ProjectReports(**data)
        self._session.add(relation)
        await self._session.flush()
        await self._session.refresh(relation)
        return relation
