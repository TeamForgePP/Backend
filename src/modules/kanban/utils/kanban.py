from datetime import date, datetime
from typing import Any, cast
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import NotificationType, TeamRole, UnitOfWork
from src.core.security.dependencies import Role
from src.modules.kanban.schemas import (
    MembersResponse,
    NewTaskRequest,
    Performer,
    SelectedSprint,
    Task,
)


class KanbanUtils:
    @classmethod
    def as_date(cls, value: Any) -> date:
        if value is None:
            raise ValueError("Expected date-like value, got None")

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return cast(date, value)

    @classmethod
    async def resolve_project(
        cls, uow: UnitOfWork, user_sub: str, user_role: Role
    ) -> tuple[UUID, str]:
        if user_role == "user":
            user_id = UUID(user_sub)
            project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )
            return project.id, project.name

        if user_role == "admin":
            projects = await uow.projects.get_all_uncompleted_projects()
            if not projects:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                )
            project = projects[0]
            return project.id, project.name

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    @classmethod
    async def resolve_current_sprint_in_project(
        cls, uow: UnitOfWork, project_id: UUID
    ) -> SelectedSprint:
        sprints = await uow.sprints.get_by_project_id(project_id)

        current: list[SelectedSprint] = []
        for sprint in sprints:
            if sprint.status == "active":
                current.append(SelectedSprint(id=sprint.id, seq=sprint.seq))

        if not current:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprints not found")

        return min(current, key=lambda s: s.seq)

    @classmethod
    async def get_performer(cls, uow: UnitOfWork, user_id: UUID) -> Performer:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return Performer(
            id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url or "",
        )

    @classmethod
    async def collect_unique_roles_for_users_in_project(
        cls,
        uow: UnitOfWork,
        project_id: UUID,
        user_ids: list[UUID],
    ) -> list[TeamRole]:
        roles_unique: list[TeamRole] = []
        for user_id in user_ids:
            roles = await uow.project_roles.get_roles_for_user_in_project(project_id, user_id)
            for role in roles:
                if role not in roles_unique:
                    roles_unique.append(role)
        return roles_unique

    @classmethod
    async def build_tasks_for_sprint(
        cls,
        uow: UnitOfWork,
        project_id: UUID,
        sprint_id: UUID,
    ) -> list[Task]:
        tasks = await uow.tasks.get_by_sprint_id(sprint_id)
        if not tasks:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found")

        tasks_response: list[Task] = []

        for task in tasks:
            assignee_ids = await uow.performes.get_assignee_ids_by_task(task.id)

            performes: list[Performer] = []
            for assignee_id in assignee_ids:
                performes.append(await cls.get_performer(uow, assignee_id))

            all_roles = await cls.collect_unique_roles_for_users_in_project(
                uow, project_id, assignee_ids
            )

            tasks_response.append(
                Task(
                    id=task.id,
                    title=task.title,
                    tags=all_roles,
                    status=task.status,
                    deadline=cls.as_date(task.deadline),
                    priority=task.priority,
                    performes=performes,
                    key=task.key,
                )
            )

        return tasks_response

    @classmethod
    async def build_members_for_project(cls, uow: UnitOfWork, project_id: UUID) -> MembersResponse:
        members = await uow.teams.get_by_project(project_id)

        members_info: list[Performer] = []
        for member in members:
            members_info.append(await cls.get_performer(uow, member.user_id))

        return MembersResponse(members=members_info)

    @classmethod
    async def resolve_sprint_for_task(
        cls,
        uow: UnitOfWork,
        project_id: UUID,
        data: NewTaskRequest,
    ) -> UUID:
        if data.sprint_id:
            sprint = await uow.sprints.get_by_id(data.sprint_id)
            if not sprint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sprint not found in project",
                )
            if sprint.project_id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sprint doesn't belong to project",
                )
            return data.sprint_id

        sprint = await uow.sprints.get_active_sprint_in_project(project_id)
        if not sprint:
            sprints = await uow.sprints.get_future_sprints_in_project(project_id)
            if not sprints:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sprints not exist",
                )
            sprint = sprints[0]

        data.sprint_id = sprint.id
        return sprint.id

    @classmethod
    async def notify_new_task(
        cls,
        uow: UnitOfWork,
        project_id: UUID,
        task_id: UUID,
        data: NewTaskRequest,
    ) -> None:
        for performer in data.performes:
            await uow.performes.add(task_id, performer.id)
            await uow.notifications.create(
                {
                    "user_id": performer.id,
                    "type": NotificationType.NewTask,
                    "title": "You have a new task",
                    "message": data.title,
                    "project_id": project_id,
                    "is_read": False,
                }
            )
