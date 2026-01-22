from datetime import date, datetime, time
from typing import Any, cast
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import NotificationType, SprintStatus, UnitOfWork
from src.core.security.dependencies import Role
from src.modules.kanban.schemas import (
    MembersResponse,
    NewTaskRequest,
    Performer,
    SelectedSprint,
    SprintItem,
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
    def deadline_to_datetime(cls, value: date | datetime) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.combine(value, time.min)

    @classmethod
    async def resolve_project(
        cls, uow: UnitOfWork, user_sub: str, user_role: Role
    ) -> tuple[UUID, str]:
        if user_role == "user":
            user_id = UUID(user_sub)
            project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )
            return project.id, project.name

        if user_role == "admin":
            projects = await uow.projects.get_all_uncompleted_projects()
            if not projects:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Projects not found",
                )
            project = projects[0]
            return project.id, project.name

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
        )

    @classmethod
    async def resolve_current_sprint_in_project(
        cls, uow: UnitOfWork, project_id: UUID
    ) -> SelectedSprint:
        sprints = await uow.sprints.get_by_project_id(project_id)

        current: list[SelectedSprint] = []
        for sprint in sprints:
            if getattr(sprint, "status", None) == SprintStatus.ACTIVE:
                current.append(SelectedSprint(id=sprint.id, seq=sprint.seq))

        if not current:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active sprint not found",
            )

        return min(current, key=lambda s: s.seq)

    @classmethod
    async def get_performer(cls, uow: UnitOfWork, user_id: UUID) -> Performer:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return Performer(
            id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url or "",
        )

    @classmethod
    async def build_tasks_for_sprint(
        cls,
        uow: UnitOfWork,
        sprint_id: UUID,
    ) -> list[Task]:
        tasks = await uow.tasks.get_by_sprint_id(sprint_id)
        if not tasks:
            return []

        tasks_response: list[Task] = []

        for task in tasks:
            assignee_ids = await uow.performes.get_assignee_ids_by_task(task.id) or []

            performers: list[Performer] = []
            for assignee_id in assignee_ids:
                performers.append(await cls.get_performer(uow, assignee_id))

            tasks_response.append(
                Task(
                    id=task.id,
                    title=task.title,
                    tag=getattr(task, "tag", None),
                    status=task.status,
                    deadline=cls.as_date(task.deadline),
                    priority=task.priority,
                    performers=performers,
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
        sprint_id = getattr(data, "sprint_id", None)

        if sprint_id is not None:
            if not isinstance(sprint_id, UUID):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Invalid sprint_id format",
                )

            sprint = await uow.sprints.get_by_id(sprint_id)
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
            return sprint_id

        sprint = await uow.sprints.get_active_sprint_in_project(project_id)
        if not sprint:
            future = await uow.sprints.get_future_sprints_in_project(project_id)
            if not future:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sprints not exist",
                )
            sprint = future[0]

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
        for performer in getattr(data, "performers", None) or []:
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

    @classmethod
    async def build_sprints_items(cls, uow: UnitOfWork, project_id: UUID) -> list[SprintItem]:
        sprints = await uow.sprints.get_by_project_id(project_id)
        return [SprintItem(id=s.id, label=f"{s.seq} — {s.name}") for s in sprints]
