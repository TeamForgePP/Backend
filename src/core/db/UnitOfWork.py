from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repositories import (
    GroupsRepo,
    InvitationsRepo,
    NotificationsRepo,
    PerformesRepo,
    ProjectReportsRepo,
    ProjectRoleRepo,
    ProjectsRepo,
    ReportsRepo,
    SprintsRepo,
    TasksRepo,
    TeamsRepo,
    UsersRepo,
)
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
        yield uow
