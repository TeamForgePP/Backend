from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, require_user_or_admin
from src.modules.home.schemas import BasicResponse, CreateProjectRequest, ProjectsResponse
from src.modules.home.services import HomeService

router = APIRouter(prefix="/user/home", tags=["home"])
user_dep = Depends(require_user_or_admin)


@router.post(
    "/new-project",
    response_model=BasicResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_project",
)
async def create_project(
    data: CreateProjectRequest, _user: PrincipalContext = user_dep
) -> BasicResponse:
    return await HomeService.create_project(data, _user.sub, _user.role)


@router.get(
    "",
    response_model=ProjectsResponse,
    status_code=status.HTTP_200_OK,
    name="get_home_info",
)
async def get_home_info(_user: PrincipalContext = user_dep) -> ProjectsResponse:
    return await HomeService.get_home_info(_user.sub, _user.role)


@router.post(
    "/{project_id}/leave",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="leave_project",
)
async def leave_project(project_id: UUID, _user: PrincipalContext = user_dep) -> BasicResponse:
    return await HomeService.leave_project(UUID(_user.sub), project_id)


@router.delete(
    "/{project_id}/delete",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="delete_project",
)
async def delete_project(project_id: UUID, _user: PrincipalContext = user_dep) -> BasicResponse:
    return await HomeService.delete_project(_user.sub, _user.role, project_id)
