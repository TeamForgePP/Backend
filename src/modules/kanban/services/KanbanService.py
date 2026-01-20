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
    SprintsResponse,
    TaskResponse,
    UpdateStatusRequest,
)
from src.modules.kanban.utils import KanbanUtils

logger = get_logger("kanban.service")
logger.setLevel(logging.INFO)


class KanbanService:
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

                tasks_response = await KanbanUtils.build_tasks_for_sprint(uow, current_sprint.id)

                return KanbanResponse(
                    project=Project(id=project_id, name=project_name),
                    selected_sprint=SelectedSprint(id=current_sprint.id, seq=current_sprint.seq),
                    tasks=tasks_response,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get_kanban_info")
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
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sprint not found",
                    )

                tasks_response = await KanbanUtils.build_tasks_for_sprint(uow, sprint_id)

                return KanbanResponse(
                    project=Project(id=project_id, name=project_name),
                    selected_sprint=SelectedSprint(id=sprint_id, seq=sprint.seq),
                    tasks=tasks_response,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get_kanban_info_by_sprint_id")
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
                logger.exception("Error during get_all_team_members")
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

                assignee_ids = await uow.performes.get_assignee_ids_by_task(task_id) or []

                performers = []
                for assignee_id in assignee_ids:
                    performers.append(await KanbanUtils.get_performer(uow, assignee_id))

                return TaskResponse(
                    id=task_id,
                    title=task.title,
                    description=task.description or "",
                    performers=performers,
                    priority=task.priority,
                    deadline=KanbanUtils.as_date(task.deadline),
                    tag=getattr(task, "tag", None),
                    key=task.key,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get_task")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    @classmethod
    async def get_number_of_sprints(cls, _user_sub: str, _user_role: Role) -> SprintsResponse:
        async with get_uow() as uow:
            try:
                project_id, _project_name = await KanbanUtils.resolve_project(
                    uow, _user_sub, _user_role
                )

                items = await KanbanUtils.build_sprints_items(uow, project_id)
                return SprintsResponse(number=len(items), sprints=items)

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get_number_of_sprints")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

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
                logger.exception("Error during task creation")
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

        sprint_id = await KanbanUtils.resolve_sprint_for_task(uow, project_id, data)

        sprint = await uow.sprints.get_by_id(sprint_id)
        if not sprint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")

        task_seq = await uow.tasks.get_next_seq_for_project(project_id)
        key = f"{sprint.seq}-{task_seq}"

        task = await uow.tasks.create(
            {
                "project_id": project_id,
                "sprint_id": sprint_id,
                "title": data.title,
                "description": data.description,
                "priority": data.priority,
                "tag": getattr(data, "tag", None),
                "status": TaskStatus.ToDo,
                "seq": task_seq,
                "key": key,
                "deadline": KanbanUtils.deadline_to_datetime(data.deadline),
            }
        )

        if data.performers:
            await KanbanUtils.notify_new_task(uow, project_id, task.id, data)

        await uow.commit()
        return BasicResponse(success=True, message="Task successfully created")

    @classmethod
    async def update_status(cls, data: UpdateStatusRequest) -> BasicResponse:
        async with get_uow() as uow:
            try:
                await uow.tasks.update(data.task_id, {"status": data.status})
                await uow.commit()
                return BasicResponse(success=True, message="Task status updated successfully")

            except Exception as e:
                logger.exception("Error during update_status")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during update status",
                ) from e
