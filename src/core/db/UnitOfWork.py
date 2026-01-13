from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repositories.GroupsRepo import GroupsRepo
from src.core.db.repositories.InvitationsRepo import InvitationsRepo
from src.core.db.repositories.NotificationsRepo import NotificationsRepo
from src.core.db.repositories.PerformesRepo import PerformesRepo
from src.core.db.repositories.ProjectReportRepo import ProjectReportsRepo
from src.core.db.repositories.ProjectRoleRepo import ProjectRoleRepo
from src.core.db.repositories.ProjectsRepo import ProjectsRepo
from src.core.db.repositories.ReportsRepo import ReportsRepo
from src.core.db.repositories.SprintsRepo import SprintsRepo
from src.core.db.repositories.TasksRepo import TasksRepo
from src.core.db.repositories.TeamsRepo import TeamsRepo
from src.core.db.repositories.UsersRepo import UsersRepo
from src.core.db.session import get_session


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

        self.tasks: TasksRepo = TasksRepo(self.session)
        self.sprints: SprintsRepo = SprintsRepo(self.session)
        self.notifications: NotificationsRepo = NotificationsRepo(self.session)
        self.invitations: InvitationsRepo = InvitationsRepo(self.session)
        self.groups: GroupsRepo = GroupsRepo(self.session)
        self.users: UsersRepo = UsersRepo(self.session)
        self.teams: TeamsRepo = TeamsRepo(self.session)
        self.reports: ReportsRepo = ReportsRepo(self.session)
        self.projects: ProjectsRepo = ProjectsRepo(self.session)
        self.project_roles: ProjectRoleRepo = ProjectRoleRepo(self.session)
        self.project_reports: ProjectReportsRepo = ProjectReportsRepo(self.session)
        self.performes: PerformesRepo = PerformesRepo(self.session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


@asynccontextmanager
async def get_uow() -> AsyncIterator[UnitOfWork]:
    async with get_session() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
        except Exception:
            await uow.rollback()
            raise
