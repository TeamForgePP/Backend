import logging
from datetime import date
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import TeamRole, UnitOfWork, get_uow
from src.core.logger import get_logger
from src.modules.home.schemas import (
    AllowedActions,
    BasicResponse,
    CreateProjectRequest,
    Project,
    ProjectsResponse,
    SprintMap,
)

logger = get_logger("home.service")
logger.setLevel(logging.INFO)


class HomeService:
    # ---------------- CREATE ---------------- #

    @classmethod
    async def create_project(
        cls,
        data: CreateProjectRequest,
    ) -> BasicResponse:
        async with get_uow() as uow:
            try:
                return await cls._create_project_in_uow(uow, data)
            except Exception as e:
                logger.error("Error during project creation: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during project creation",
                ) from e

    @classmethod
    async def _create_project_in_uow(
        cls, uow: UnitOfWork, data: CreateProjectRequest
    ) -> BasicResponse:
        logger.info("create_project started | name=%s", data.name)

        existing_project = await uow.projects.get_by_name(data.name)
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Project with this name already exist"
            )

        project = await uow.projects.create(
            {
                "name": data.name,
                "description": data.description,
                "git_organization": data.git_organization,
            }
        )

        for team_member in data.team:
            for role in team_member.roles:
                if role not in TeamRole:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="Invalid team role format",
                    )
                else:
                    await uow.project_roles.add_role(
                        project_id=project.id,
                        user_id=team_member.id,
                        role=role,
                    )

        await uow.commit()

        return BasicResponse(success=True, message="Project successfully created")

    # ---------------- GET ---------------- #

    @classmethod
    async def get_home_info(cls, user_id: UUID) -> ProjectsResponse:
        async with get_uow() as uow:
            try:
                logger.info("get_home_info started")

                projects = await uow.projects.get_projects_id_by_user_id(user_id)
                projects_response: list[Project] = []

                for project in projects:
                    roles = await uow.project_roles.get_roles_for_user_in_project(
                        project.id, user_id
                    )

                    sprints = await uow.sprints.get_by_project_id(project.id)

                    sprints_map = []
                    current_sprints = []

                    for sprint in sprints:
                        sprint_map = SprintMap(
                            id=sprint.id,
                            name=sprint.name,
                            seq=sprint.seq,
                            deadline=sprint.deadline,  # type: ignore
                        )
                        sprints_map.append(sprint_map)

                        if sprint.start <= date.today() <= sprint.deadline:  # type: ignore
                            current_sprints.append(sprint_map)

                    if current_sprints:
                        current_sprint = min(current_sprints, key=lambda s: s.seq)
                    else:
                        current_sprint = None

                    if current_sprint:
                        current_sprint_seq = current_sprint.seq
                        current_sprint_name = current_sprint.name
                        nearest_deadline = current_sprint.deadline
                    else:
                        current_sprint_seq = 0
                        current_sprint_name = ""
                        nearest_deadline = None

                    allowed_actions = AllowedActions(
                        can_delete=TeamRole.TeamLead in roles, can_leave=True
                    )

                    project_info = Project(
                        id=project.id,
                        name=project.name,
                        is_completed=project.is_completed,
                        current_sprint_name=current_sprint_name,
                        current_sprint_seq=current_sprint_seq,
                        role=roles,
                        nearest_deadline=nearest_deadline,
                        sprint_map=sprints_map,
                        allowed_actions=allowed_actions,
                    )

                    projects_response.append(project_info)

                return ProjectsResponse(projects=projects_response)

            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    # ---------------- LEAVE ---------------- #

    @classmethod
    async def leave_project(cls, user_id: UUID, project_id: UUID) -> BasicResponse:
        async with get_uow() as uow:
            logger.info("leave_project started | project_id=%s", project_id)

            project = await uow.projects.get_by_id(project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )

            user_roles = await uow.project_roles.get_roles_for_user_in_project(
                project_id=project_id, user_id=user_id
            )
            if not user_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
            for role in user_roles:
                await uow.project_roles.delete_role(
                    project_id=project_id, user_id=user_id, role=role
                )

            await uow.commit()

            return BasicResponse(success=True, message="You left the project successfully")

    # ---------------- DELETE ---------------- #

    @classmethod
    async def delete_project(cls, user_id: UUID, project_id: UUID) -> BasicResponse:
        async with get_uow() as uow:
            logger.info("delete_project started | project_id=%s", project_id)

            exists = await uow.projects.get_by_id(project_id)
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or already deleted",
                )

            user_roles = await uow.project_roles.get_roles_for_user_in_project(
                project_id=project_id, user_id=user_id
            )

            if TeamRole.TeamLead not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only team lead can delete project",
                )

            deleted = await uow.projects.delete(project_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete project",
                )

            await uow.commit()

            return BasicResponse(success=True, message="Project successfully deleted")
