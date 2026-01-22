from datetime import date, datetime
from typing import Any, cast
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import SprintStatus, UnitOfWork
from src.core.security.dependencies import Role
from src.modules.sprints.schemas import CurrentSprint, FutureCompletedSprint, Sprint


class SprintsUtils:
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
    async def pick_uncompleted_project(cls, uow: UnitOfWork, user_sub: str, user_role: Role) -> Any:
        if user_role == "user":
            user_id = UUID(user_sub)
            project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="You don't have uncompleted project",
                )
            return project

        if user_role == "admin":
            projects = await uow.projects.get_all_uncompleted_projects()
            if not projects:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Projects not found",
                )
            return projects[0]

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    @classmethod
    def bucketize_sprints(
        cls, sprints: list[Any]
    ) -> tuple[CurrentSprint | None, list[FutureCompletedSprint], list[FutureCompletedSprint]]:
        current: CurrentSprint | None = None
        future: list[FutureCompletedSprint] = []
        completed: list[FutureCompletedSprint] = []

        for sprint in sprints:
            if sprint.status == SprintStatus.ACTIVE:
                current = CurrentSprint(
                    id=sprint.id,
                    seq=sprint.seq,
                    name=sprint.name,
                    goal=sprint.goal or "",
                    description=sprint.description or "",
                    estimated_deadline=cls.as_date(sprint.deadline),
                )
            elif sprint.status == SprintStatus.UPCOMING:
                future.append(FutureCompletedSprint(id=sprint.id, seq=sprint.seq, name=sprint.name))
            else:
                completed.append(
                    FutureCompletedSprint(id=sprint.id, seq=sprint.seq, name=sprint.name)
                )

        return current, future, completed

    @classmethod
    def sprint_update_payload(cls, data: Sprint) -> dict[str, Any]:
        return {
            "name": data.name,
            "start": data.start_date,
            "deadline": data.end_date,
            "goal": data.goal,
            "description": data.description,
        }

    @classmethod
    def sprint_create_payload(
        cls,
        project_id: UUID,
        seq: int,
        data: Sprint,
        status: SprintStatus,
    ) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "seq": seq,
            "name": data.name,
            "description": data.description,
            "goal": data.goal,
            "start": data.start_date,
            "deadline": data.end_date,
            "status": status,
        }
