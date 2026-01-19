from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, require_user_or_admin
from src.modules.home.schemas import (
    BasicResponse,
    CreateProjectRequest,
    ProjectsResponse,
    UsersResponse,
)
from src.modules.home.services import HomeService

router = APIRouter(prefix="/projects", tags=["projects"])
user_dep = Depends(require_user_or_admin)


@router.post(
    "",
    response_model=BasicResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_project",
)
async def create_project(
    data: CreateProjectRequest,
    _user: PrincipalContext = user_dep,
) -> BasicResponse:
    return await HomeService.create_project(data, _user.sub, _user.role)


@router.get(
    "",
    response_model=ProjectsResponse,
    status_code=status.HTTP_200_OK,
    name="get_projects",
)
async def get_projects(_user: PrincipalContext = user_dep) -> ProjectsResponse:
    return await HomeService.get_home_info(_user.sub, _user.role)


@router.get(
    "/users-for-team",
    response_model=UsersResponse,
    status_code=status.HTTP_200_OK,
    name="get_users_for_team",
)
async def get_users_for_team(_user: PrincipalContext = user_dep) -> UsersResponse:
    return await HomeService.get_users_for_team(_user.sub, _user.role)


@router.post(
    "/{project_id}/leave",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="leave_project",
)
async def leave_project(
    project_id: UUID,
    _user: PrincipalContext = user_dep,
) -> BasicResponse:
    return await HomeService.leave_project(UUID(_user.sub), project_id)


@router.delete(
    "/{project_id}",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="delete_project",
)
async def delete_project(
    project_id: UUID,
    _user: PrincipalContext = user_dep,
) -> BasicResponse:
    return await HomeService.delete_project(_user.sub, _user.role, project_id)
