import logging
from typing import cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.core.db import get_uow
from src.core.db.models import Groups, Users
from src.core.logger import get_logger
from src.modules.admin.schemas import GroupCreate, GroupRead, GroupUpdate, UserRead
from src.modules.admin.utils import group_to_read_model, user_to_read_model

logger = get_logger("admin.group.service")
logger.setLevel(logging.INFO)


class GroupService:
    @classmethod
    async def create_group(cls, data: GroupCreate) -> GroupRead:
        try:
            async with get_uow() as uow:
                group = await uow.groups.create(data.model_dump())
                await uow.commit()
                return group_to_read_model(cast(Groups, group))
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Group already exists",
            ) from e
        except Exception as e:
            logger.error("Error during group creation: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during group creation",
            ) from e

    @classmethod
    async def get_group_by_id(cls, group_id: UUID) -> GroupRead:
        async with get_uow() as uow:
            group = await uow.groups.get_by_id(group_id)
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found",
                )
            return group_to_read_model(cast(Groups, group))

    @classmethod
    async def get_all_groups(cls) -> list[GroupRead]:
        async with get_uow() as uow:
            groups = await uow.groups.get_all()
            return [group_to_read_model(cast(Groups, g)) for g in groups]

    @classmethod
    async def get_students_in_group(cls, group_id: UUID) -> list[UserRead]:
        async with get_uow() as uow:
            group = await uow.groups.get_by_id(group_id)
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found",
                )

            students = await uow.users.get_by_group(group_id)
            return [user_to_read_model(cast(Users, u)) for u in students]

    @classmethod
    async def update_group(cls, group_id: UUID, data: GroupUpdate) -> GroupRead:
        try:
            async with get_uow() as uow:
                update_data = data.model_dump(exclude_unset=True)
                updated = await uow.groups.update(group_id, update_data)
                if not updated:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Group not found",
                    )

                await uow.commit()
                return group_to_read_model(cast(Groups, updated))
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Group with this name already exists",
            ) from e
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error during group update: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during group update",
            ) from e

    @classmethod
    async def delete_group(cls, group_id: UUID) -> None:
        async with get_uow() as uow:
            deleted = await uow.groups.delete(group_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found",
                )
            await uow.commit()
