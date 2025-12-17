from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import AccessContext, require_admin
from src.modules.home.schemas import BasicResponse, CreateProjectRequest, ProjectsResponse
from src.modules.home.services import HomeService

router = APIRouter(prefix="/user/home", tags=["home"])
admin_dep = Depends(require_admin)


@router.post(
    "/new-project",
    response_model=BasicResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_project",
)
async def create_project(
    data: CreateProjectRequest, _admin: AccessContext = admin_dep
) -> BasicResponse:
    return await HomeService.create_project(data, UUID(_admin.sub))


@router.get(
    "",
    response_model=ProjectsResponse,
    status_code=status.HTTP_200_OK,
    name="get_home_info",
)
async def get_home_info(_admin: AccessContext = admin_dep) -> ProjectsResponse:
    return await HomeService.get_home_info(UUID(_admin.sub), access=admin_dep)


@router.post(
    "/{project_id}/leave",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="leave_project",
)
async def leave_project(project_id: UUID, _admin: AccessContext = admin_dep) -> BasicResponse:
    return await HomeService.leave_project(UUID(_admin.sub), project_id)


@router.delete(
    "/{project_id}/delete",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="delete_project",
)
async def delete_project(project_id: UUID, _admin: AccessContext = admin_dep) -> BasicResponse:
    return await HomeService.delete_project(UUID(_admin.sub), project_id, access=admin_dep)
