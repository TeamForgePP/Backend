import logging
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import TaskStatus, UnitOfWork, get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import Role
from src.modules.kanban.schemas import (
    BasicResponse,
    KanbanResponse,
    MembersResponse,
    NewTaskRequest,
    Project,
    SelectedSprint,
    TaskResponse,
    UpdateStatusRequest,
)
from src.modules.kanban.utils import KanbanUtils

logger = get_logger("home.service")
logger.setLevel(logging.INFO)


class KanbanService:
    # ---------------- GET ---------------- #

    @classmethod
    async def get_kanban_info(cls, _user_sub: str, _user_role: Role) -> KanbanResponse:
        async with get_uow() as uow:
            try:
                project_id, project_name = await KanbanUtils.resolve_project(
                    uow, _user_sub, _user_role
                )

                current_sprint = await KanbanUtils.resolve_current_sprint_in_project(
                    uow, project_id
                )
                tasks_response = await KanbanUtils.build_tasks_for_sprint(
                    uow, project_id, current_sprint.id
                )

                return KanbanResponse(
                    project=Project(id=project_id, name=project_name),
                    selected_sprint=SelectedSprint(id=current_sprint.id, seq=current_sprint.seq),
                    tasks=tasks_response,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    @classmethod
    async def get_kanban_info_by_sprint_id(
        cls, _user_sub: str, _user_role: Role, sprint_id: UUID
    ) -> KanbanResponse:
        async with get_uow() as uow:
            try:
                project_id, project_name = await KanbanUtils.resolve_project(
                    uow, _user_sub, _user_role
                )

                sprint = await uow.sprints.get_by_id(sprint_id)
                if not sprint:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
                    )

                tasks_response = await KanbanUtils.build_tasks_for_sprint(
                    uow, project_id, sprint_id
                )

                return KanbanResponse(
                    project=Project(id=project_id, name=project_name),
                    selected_sprint=SelectedSprint(id=sprint_id, seq=sprint.seq),
                    tasks=tasks_response,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    @classmethod
    async def get_all_team_members(cls, _user_sub: str, _user_role: Role) -> MembersResponse:
        async with get_uow() as uow:
            try:
                project_id, _project_name = await KanbanUtils.resolve_project(
                    uow, _user_sub, _user_role
                )
                return await KanbanUtils.build_members_for_project(uow, project_id)

            except HTTPException:
                raise
            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    @classmethod
    async def get_task(cls, task_id: UUID) -> TaskResponse:
        async with get_uow() as uow:
            try:
                task = await uow.tasks.get_by_id(task_id)
                if not task:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
                    )

                assignee_ids = await uow.performes.get_assignee_ids_by_task(task_id)

                users_response = []
                for assignee_id in assignee_ids:
                    users_response.append(await KanbanUtils.get_performer(uow, assignee_id))

                return TaskResponse(
                    id=task_id,
                    title=task.title,
                    description=task.description or "",
                    users=users_response,
                    priority=task.priority,
                    deadline=KanbanUtils.as_date(task.deadline),
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    # ---------------- CREATE ---------------- #

    @classmethod
    async def create_task(
        cls, data: NewTaskRequest, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        async with get_uow() as uow:
            try:
                return await cls._create_task_in_uow(uow, data, _user_sub, _user_role)
            except HTTPException:
                raise
            except Exception as e:
                logger.error("Error during task creation: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during task creation",
                ) from e

    @classmethod
    async def _create_task_in_uow(
        cls,
        uow: UnitOfWork,
        data: NewTaskRequest,
        _user_sub: str,
        _user_role: Role,
    ) -> BasicResponse:
        logger.info("create_task started")

        project_id, _project_name = await KanbanUtils.resolve_project(uow, _user_sub, _user_role)

        performer_ids: list[UUID] = [p.id for p in data.performes]
        all_roles = await KanbanUtils.collect_unique_roles_for_users_in_project(
            uow, project_id, performer_ids
        )

        sprint_id = await KanbanUtils.resolve_sprint_for_task(uow, project_id, data)

        task = await uow.tasks.create(
            {
                "project_id": project_id,
                "sprint_id": sprint_id,
                "title": data.title,
                "description": data.description,
                "priority": data.priority,
                "tag": all_roles,
                "status": TaskStatus.ToDo,
                "deadline": data.deadline,
            }
        )

        await KanbanUtils.notify_new_task(uow, project_id, task.id, data)

        await uow.commit()
        return BasicResponse(success=True, message="Task successfully created")

    # ---------------- POST ---------------- #

    @classmethod
    async def update_status(cls, data: UpdateStatusRequest) -> BasicResponse:
        async with get_uow() as uow:
            try:
                await uow.tasks.update(data.task_id, {"status": data.status})
                await uow.commit()
                return BasicResponse(success=True, message="Task status updated successfully")

            except Exception as e:
                logger.error("Error during update status: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during update status",
                ) from e
