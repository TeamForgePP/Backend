from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import AccessContext, require_admin
from src.modules.admin.schemas import GroupCreate, GroupRead, GroupUpdate, UserRead
from src.modules.admin.services.GroupService import GroupService

router = APIRouter(prefix="/admin/groups", tags=["admin"])
admin_dep = Depends(require_admin)


@router.post(
    "",
    response_model=GroupRead,
    status_code=status.HTTP_201_CREATED,
    name="admin_create_group",
)
async def create_group(
    data: GroupCreate,
    _admin: AccessContext = admin_dep,
) -> GroupRead:
    return await GroupService.create_group(data)


@router.get(
    "",
    response_model=list[GroupRead],
    status_code=status.HTTP_200_OK,
    name="admin_get_all_groups",
)
async def get_all_groups(
    _admin: AccessContext = admin_dep,
) -> list[GroupRead]:
    return await GroupService.get_all_groups()


@router.get(
    "/{group_id}",
    response_model=GroupRead,
    status_code=status.HTTP_200_OK,
    name="admin_get_group_by_id",
)
async def get_group_by_id(
    group_id: UUID,
    _admin: AccessContext = admin_dep,
) -> GroupRead:
    return await GroupService.get_group_by_id(group_id)


@router.get(
    "/{group_id}/students",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    name="admin_get_group_students",
)
async def get_group_students(
    group_id: UUID,
    _admin: AccessContext = admin_dep,
) -> list[UserRead]:
    return await GroupService.get_students_in_group(group_id)


@router.patch(
    "/{group_id}",
    response_model=GroupRead,
    status_code=status.HTTP_200_OK,
    name="admin_update_group",
)
async def update_group(
    group_id: UUID,
    data: GroupUpdate,
    _admin: AccessContext = admin_dep,
) -> GroupRead:
    return await GroupService.update_group(group_id, data)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="admin_delete_group",
)
async def delete_group(
    group_id: UUID,
    _admin: AccessContext = admin_dep,
) -> None:
    await GroupService.delete_group(group_id)
