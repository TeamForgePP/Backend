from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, require_user_or_admin
from src.modules.kanban.schemas import (
    KanbanResponse,
    MembersResponse,
    NewTaskRequest,
    SprintsResponse,
    TaskResponse,
    UpdateStatusRequest,
)
from src.modules.kanban.schemas.kanban import BasicResponse
from src.modules.kanban.services import KanbanService

router = APIRouter(prefix="/kanban", tags=["kanban"])
user_dep = Depends(require_user_or_admin)


@router.get(
    "",
    response_model=KanbanResponse,
    status_code=status.HTTP_200_OK,
    name="get_kanban_info",
)
async def get_kanban_info(_user: PrincipalContext = user_dep) -> KanbanResponse:
    return await KanbanService.get_kanban_info(_user.sub, _user.role)


@router.get(
    "/team-members",
    response_model=MembersResponse,
    status_code=status.HTTP_200_OK,
    name="get_all_team_members",
)
async def get_all_team_members(_user: PrincipalContext = user_dep) -> MembersResponse:
    return await KanbanService.get_all_team_members(_user.sub, _user.role)


@router.get(
    "/sprints",
    response_model=SprintsResponse,
    status_code=status.HTTP_200_OK,
    name="get_number_of_sprints",
)
async def get_number_of_sprints(_user: PrincipalContext = user_dep) -> SprintsResponse:
    return await KanbanService.get_number_of_sprints(_user.sub, _user.role)


@router.get(
    "/sprints/{sprint_id}",
    response_model=KanbanResponse,
    status_code=status.HTTP_200_OK,
    name="get_kanban_by_sprint_id",
)
async def get_kanban_by_sprint_id(
    sprint_id: UUID,
    _user: PrincipalContext = user_dep,
) -> KanbanResponse:
    return await KanbanService.get_kanban_info_by_sprint_id(_user.sub, _user.role, sprint_id)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    name="get_task",
)
async def get_task(task_id: UUID, _user: PrincipalContext = user_dep) -> TaskResponse:
    return await KanbanService.get_task(task_id)


@router.post(
    "/new-task",
    response_model=BasicResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_task",
)
async def create_task(data: NewTaskRequest, _user: PrincipalContext = user_dep) -> BasicResponse:
    return await KanbanService.create_task(data, _user.sub, _user.role)


@router.post(
    "/update-status",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="update_status",
)
async def update_status(
    data: UpdateStatusRequest,
    _user: PrincipalContext = user_dep,
) -> BasicResponse:
    return await KanbanService.update_status(data)
