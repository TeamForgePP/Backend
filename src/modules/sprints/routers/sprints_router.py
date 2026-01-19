from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, require_user_or_admin
from src.modules.sprints.schemas import AllSprintsResponse, BasicResponse, Sprint
from src.modules.sprints.services import SprintsService

router = APIRouter(prefix="/sprints", tags=["sprints"])
user_dep = Depends(require_user_or_admin)


@router.get(
    "",
    response_model=AllSprintsResponse,
    status_code=status.HTTP_200_OK,
    name="get_sprints",
)
async def get_sprints_info(_user: PrincipalContext = user_dep) -> AllSprintsResponse:
    return await SprintsService.get_sprints_info(_user.sub, _user.role)


@router.post(
    "/new-sprint",
    response_model=BasicResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_sprint",
)
async def create_sprint(data: Sprint, _user: PrincipalContext = user_dep) -> BasicResponse:
    return await SprintsService.create_sprint(data, _user.sub, _user.role)


@router.get(
    "/{sprint_id}",
    response_model=Sprint,
    status_code=status.HTTP_200_OK,
    name="get_sprint_by_id",
)
async def get_sprint_by_id(sprint_id: UUID) -> Sprint:
    return await SprintsService.get_sprint_by_id(sprint_id)


@router.patch(
    "/{sprint_id}",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="edit_sprint",
)
async def edit_sprint(data: Sprint, sprint_id: UUID) -> BasicResponse:
    return await SprintsService.edit_sprint(sprint_id, data)


@router.post(
    "/{sprint_id}/complete",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="complete_sprint_and_start_new",
)
async def complete_sprint(sprint_id: UUID) -> BasicResponse:
    return await SprintsService.complete_sprint(sprint_id)
