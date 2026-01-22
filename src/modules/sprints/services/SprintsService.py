import logging
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import SprintStatus, UnitOfWork, get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import Role
from src.modules.sprints.schemas import AllSprintsResponse, BasicResponse, Sprint
from src.modules.sprints.utils import SprintsUtils

logger = get_logger("sprints.service")
logger.setLevel(logging.INFO)


class SprintsService:
    # ---------------- GET ---------------- #

    @classmethod
    async def get_sprints_info(cls, _user_sub: str, _user_role: Role) -> AllSprintsResponse:
        async with get_uow() as uow:
            try:
                project = await SprintsUtils.pick_uncompleted_project(uow, _user_sub, _user_role)
                sprints = await uow.sprints.get_by_project_id(project.id)

                current_sprint, future_sprints, completed_sprints = SprintsUtils.bucketize_sprints(
                    sprints
                )

                return AllSprintsResponse(
                    current_sprint=current_sprint,
                    future_sprints=future_sprints,
                    completed_sprints=completed_sprints,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get_sprints_info")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get sprints",
                ) from e

    @classmethod
    async def get_sprint_by_id(cls, sprint_id: UUID) -> Sprint:
        async with get_uow() as uow:
            try:
                sprint = await uow.sprints.get_by_id(sprint_id)
                if not sprint:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sprint not found",
                    )

                return Sprint(
                    name=sprint.name,
                    start_date=SprintsUtils.as_date(sprint.start),
                    end_date=SprintsUtils.as_date(sprint.deadline),
                    goal=sprint.goal or "",
                    description=sprint.description or "",
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get_sprint_by_id")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get sprint",
                ) from e

    # ---------------- EDIT ---------------- #

    @classmethod
    async def edit_sprint(cls, sprint_id: UUID, data: Sprint) -> BasicResponse:
        async with get_uow() as uow:
            try:
                updated = await uow.sprints.update(
                    sprint_id, SprintsUtils.sprint_update_payload(data)
                )
                if updated is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sprint not found",
                    )

                await uow.commit()
                return BasicResponse(success=True, message="Sprint successfully edited")

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during edit_sprint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during edit sprint",
                ) from e

    # ---------------- COMPLETE ---------------- #

    @classmethod
    async def complete_sprint(cls, sprint_id: UUID) -> BasicResponse:
        async with get_uow() as uow:
            try:
                sprint = await uow.sprints.get_by_id(sprint_id)
                if not sprint:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sprint not found",
                    )

                if sprint.status != SprintStatus.ACTIVE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Sprint cannot be completed",
                    )

                future_sprints = await uow.sprints.get_future_sprints_in_project(sprint.project_id)
                if not future_sprints:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot complete sprint: no upcoming sprint found",
                    )

                next_sprint = future_sprints[0]

                await uow.sprints.update(sprint_id, {"status": SprintStatus.COMPLETED})
                await uow.sprints.update(next_sprint.id, {"status": SprintStatus.ACTIVE})

                await uow.commit()
                return BasicResponse(success=True, message="Sprint successfully completed")

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during complete_sprint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during complete sprint",
                ) from e

    # ---------------- CREATE ---------------- #

    @classmethod
    async def create_sprint(cls, data: Sprint, _user_sub: str, _user_role: Role) -> BasicResponse:
        async with get_uow() as uow:
            try:
                return await cls._create_sprint_in_uow(uow, data, _user_sub, _user_role)
            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during sprint creation")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during sprint creation",
                ) from e

    @classmethod
    async def _create_sprint_in_uow(
        cls,
        uow: UnitOfWork,
        data: Sprint,
        _user_sub: str,
        _user_role: Role,
    ) -> BasicResponse:
        logger.info("create_sprint started")

        project = await SprintsUtils.pick_uncompleted_project(uow, _user_sub, _user_role)

        seq = await uow.sprints.get_next_seq_for_project(project.id)

        active = await uow.sprints.get_active_sprint_in_project(project.id)
        new_status = SprintStatus.ACTIVE if active is None else SprintStatus.UPCOMING

        payload = SprintsUtils.sprint_create_payload(project.id, seq, data, new_status)
        await uow.sprints.create(payload)

        await uow.commit()
        return BasicResponse(success=True, message="Sprint successfully created")
