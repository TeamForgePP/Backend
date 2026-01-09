import logging
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import SprintStatus, UnitOfWork, get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import Role
from src.modules.sprints.schemas import (
    AllSprintsResponse,
    BasicResponse,
    CurrentSprint,
    FutureCompletedSprint,
    Sprint,
)

logger = get_logger("home.service")
logger.setLevel(logging.INFO)


class SprintsService:
    # ---------------- GET ---------------- #

    @classmethod
    async def get_sprints_info(cls, _user_sub: str, _user_role: Role) -> AllSprintsResponse:
        async with get_uow() as uow:
            try:
                if _user_role == "user":
                    user_id = UUID(_user_sub)
                    project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
                    if not project:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="You don't have uncompleted project",
                        )

                    sprints = await uow.sprints.get_by_project_id(project.id)

                    current_sprint: CurrentSprint | None = None
                    future_sprints: list[FutureCompletedSprint] = []
                    completed_sprints: list[FutureCompletedSprint] = []

                    for sprint in sprints:
                        if sprint.status == SprintStatus.ACTIVE:
                            current_sprint = CurrentSprint(
                                id=sprint.id,
                                seq=sprint.seq,
                                name=sprint.name,
                                goal=sprint.goal or "",
                                description=sprint.description or "",
                                estimated_deadline=sprint.deadline,  # type: ignore
                            )
                        elif sprint.status == SprintStatus.UPCOMING:
                            future_sprint = FutureCompletedSprint(
                                id=sprint.id, seq=sprint.seq, name=sprint.name
                            )
                            future_sprints.append(future_sprint)
                        else:
                            completed_sprint = FutureCompletedSprint(
                                id=sprint.id, seq=sprint.seq, name=sprint.name
                            )
                            completed_sprints.append(completed_sprint)

                    response = AllSprintsResponse(
                        current_sprint=current_sprint,
                        future_sprints=future_sprints,
                        completed_sprints=completed_sprints,
                    )

                    return response

                elif _user_role == "admin":
                    projects = await uow.projects.get_all_uncompleted_projects()
                    if not projects:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                        )
                    project = projects[0]

                    sprints = await uow.sprints.get_by_project_id(project.id)

                    current_sprint: CurrentSprint | None = None
                    future_sprints: list[FutureCompletedSprint] = []
                    completed_sprints: list[FutureCompletedSprint] = []

                    for sprint in sprints:
                        if sprint.status == SprintStatus.ACTIVE:
                            current_sprint = CurrentSprint(
                                id=sprint.id,
                                seq=sprint.seq,
                                name=sprint.name,
                                goal=sprint.goal or "",
                                description=sprint.description or "",
                                estimated_deadline=sprint.deadline,  # type: ignore
                            )
                        elif sprint.status == SprintStatus.UPCOMING:
                            future_sprint = FutureCompletedSprint(
                                id=sprint.id, seq=sprint.seq, name=sprint.name
                            )
                            future_sprints.append(future_sprint)
                        else:
                            completed_sprint = FutureCompletedSprint(
                                id=sprint.id, seq=sprint.seq, name=sprint.name
                            )
                            completed_sprints.append(completed_sprint)

                    response = AllSprintsResponse(
                        current_sprint=current_sprint,
                        future_sprints=future_sprints,
                        completed_sprints=completed_sprints,
                    )

                    return response

                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
                    )

            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    @classmethod
    async def get_sprint_by_id(cls, sprint_id: UUID) -> Sprint:
        async with get_uow() as uow:
            try:
                sprint = await uow.sprints.get_by_id(sprint_id)
                if not sprint:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
                    )

                response = Sprint(
                    name=sprint.name,
                    start_date=sprint.start,  # type: ignore
                    end_date=sprint.deadline,  # type: ignore
                    goal=sprint.goal or "",
                    description=sprint.description or "",
                )

                return response

            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    # ---------------- EDIT ---------------- #

    @classmethod
    async def edit_sprint(cls, sprint_id: UUID, data: Sprint) -> BasicResponse:
        async with get_uow() as uow:
            try:
                data_update = {
                    "name": data.name,
                    "start_date": data.start_date,
                    "end_date": data.end_date,
                    "goal": data.goal,
                    "description": data.description,
                }
                await uow.sprints.update(sprint_id, data_update)
                await uow.commit()
                return BasicResponse(success=True, message="Sprint successfully edited")

            except Exception as e:
                logger.error("Error during edit sprint: %s", str(e))
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
                        status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
                    )
                if sprint.status != SprintStatus.ACTIVE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail="Sprint cannot completed"
                    )

                await uow.sprints.update(sprint_id, {"status": SprintStatus.COMPLETED})

                sprints = await uow.sprints.get_future_sprints_in_project(sprint.project_id)
                if sprints:
                    future_sprint = sprints[0]
                    await uow.sprints.update(future_sprint.id, {"status": SprintStatus.ACTIVE})

                await uow.commit()
                return BasicResponse(success=True, message="Sprint successfully completed")

            except Exception as e:
                logger.error("Error during complete sprint: %s", str(e))
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
            except Exception as e:
                logger.error("Error during sprint creation: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during sprint creation",
                ) from e

    @classmethod
    async def _create_sprint_in_uow(
        cls, uow: UnitOfWork, data: Sprint, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        logger.info("create_sprint started")

        if _user_role == "user":
            user_id = UUID(_user_sub)
            project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="You don't have uncompleted project",
                )

            await uow.sprints.create(
                {
                    "project_id": project.id,
                    "name": data.name,
                    "description": data.description,
                    "goal": data.goal,
                    "start": data.start_date,
                    "deadline": data.end_date,
                }
            )

            await uow.commit()
            return BasicResponse(success=True, message="Sprint successfully created")

        elif _user_role == "admin":
            projects = await uow.projects.get_all_uncompleted_projects()
            if not projects:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                )
            project = projects[0]

            await uow.sprints.create(
                {
                    "project_id": project.id,
                    "name": data.name,
                    "description": data.description,
                    "goal": data.goal,
                    "start": data.start_date,
                    "deadline": data.end_date,
                }
            )

            await uow.commit()
            return BasicResponse(success=True, message="Sprint successfully created")

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
            )
