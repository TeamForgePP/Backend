import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import (
    InvitationStatus,
    NotificationType,
    TeamRole,
    UnitOfWork,
    UserStatus,
    get_uow,
)
from src.core.logger import get_logger
from src.core.security.dependencies import AccessContext
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
    async def create_project(cls, data: CreateProjectRequest, user_id: UUID) -> BasicResponse:
        async with get_uow() as uow:
            try:
                return await cls._create_project_in_uow(uow, data, user_id)
            except Exception as e:
                logger.error("Error during project creation: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during project creation",
                ) from e

    @classmethod
    async def _create_project_in_uow(
        cls, uow: UnitOfWork, data: CreateProjectRequest, user_id: UUID
    ) -> BasicResponse:
        logger.info("create_project started | name=%s", data.name)

        project = await uow.projects.create(
            {
                "teamlead_id": user_id,
                "name": data.name,
                "description": data.description,
                "git_organization": data.git_organization,
                "created_at": datetime.now(UTC),
            }
        )

        await uow.teams.create(
            {
                "project_id": project.id,
                "user_id": user_id,
                "status": UserStatus.Owner,
                "created_at": datetime.now(UTC),
            }
        )

        await uow.project_roles.add_role(
            project_id=project.id, user_id=user_id, role=TeamRole.TeamLead
        )

        for team_member in data.team:
            if team_member.id == user_id:
                continue

            if team_member.roles:
                for role in team_member.roles:
                    if role not in TeamRole:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Invalid team role format",
                        )
                    elif role == TeamRole.TeamLead:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Only one team lead can be",
                        )
                    else:
                        await uow.project_roles.add_role(
                            project_id=project.id,
                            user_id=team_member.id,
                            role=role,
                        )

            await uow.teams.create(
                {
                    "project_id": project.id,
                    "user_id": team_member.id,
                    "status": UserStatus.Invited,
                    "created_at": datetime.now(UTC),
                }
            )

            new_notification = await uow.notifications.create(
                {
                    "user_id": team_member.id,
                    "type": NotificationType.NewInvite,
                    "project_id": project.id,
                    "created_at": datetime.now(UTC),
                }
            )

            await uow.invitations.create(
                {
                    "notification_id": new_notification.id,
                    "project_id": project.id,
                    "invited_user_id": team_member.id,
                    "invited_by_id": user_id,
                    "status": InvitationStatus.Posted,
                    "created_at": datetime.now(UTC),
                }
            )

        await uow.commit()

        return BasicResponse(success=True, message="Project successfully created")

    # ---------------- GET ---------------- #

    @classmethod
    async def get_home_info(cls, user_id: UUID, access: AccessContext) -> ProjectsResponse:
        async with get_uow() as uow:
            try:
                logger.info("get_home_info started")

                projects = await uow.projects.get_projects_id_by_user_id(user_id)

                if not projects:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                    )

                projects_response: list[Project] = []

                for project in projects:
                    roles = await uow.project_roles.get_roles_for_user_in_project(
                        project.id, user_id
                    )

                    sprints = await uow.sprints.get_by_project_id(project.id)

                    sprints_map = []
                    current_sprints = []

                    for sprint in sprints:
                        if sprint.status == "active":
                            sprints_map.append(
                                SprintMap(
                                    id=sprint.id,
                                    name=sprint.name,
                                    seq=sprint.seq,
                                    active=True,
                                    deadline=sprint.deadline,  # type: ignore
                                )
                            )
                            current_sprints.append(
                                SprintMap(
                                    id=sprint.id,
                                    name=sprint.name,
                                    seq=sprint.seq,
                                    active=True,
                                    deadline=sprint.deadline,  # type: ignore
                                )
                            )
                        else:
                            sprints_map.append(
                                SprintMap(
                                    id=sprint.id,
                                    name=sprint.name,
                                    seq=sprint.seq,
                                    deadline=sprint.deadline,  # type: ignore
                                )
                            )

                    if current_sprints:
                        current_sprint = min(current_sprints, key=lambda s: s.seq)
                        current_sprint_seq = current_sprint.seq
                        current_sprint_name = current_sprint.name
                    else:
                        current_sprint_seq = 0
                        current_sprint_name = ""

                    tasks = await uow.tasks.get_by_project(project.id)
                    deadlines = []
                    for task in tasks:
                        assignees = await uow.performes.get_assignee_ids_by_task(task.id)
                        if user_id in assignees:
                            deadlines.append(task.deadline)
                    if deadlines:
                        nearest_deadline = min(deadlines)  # type: ignore
                    else:
                        nearest_deadline = None

                    allowed_actions = AllowedActions(
                        can_delete=((TeamRole.TeamLead in roles) or (access.role == "admin")),
                        can_leave=True,
                    )

                    project_info = Project(
                        id=project.id,
                        name=project.name,
                        is_completed=project.is_completed,
                        current_sprint_name=current_sprint_name,
                        current_sprint_seq=current_sprint_seq,
                        role=roles,
                        nearest_deadline=nearest_deadline,  # type:ignore
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

            roles = await uow.project_roles.get_roles_for_user_in_project(
                project_id=project_id, user_id=user_id
            )
            if not roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="You're not a project member"
                )

            if project.teamlead_id == user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Teamlead can't leave project"
                )

            await uow.project_roles.delete_all_roles(project_id=project_id, user_id=user_id)

            await uow.teams.delete_member(project_id=project_id, user_id=user_id)
            await uow.invitations.delete_all_user_invitations(
                project_id=project_id, user_id=user_id
            )
            await uow.notifications.delete_all_user_notifications(
                project_id=project_id, user_id=user_id
            )

            await uow.commit()

            return BasicResponse(success=True, message="You left the project successfully")

    # ---------------- DELETE ---------------- #

    @classmethod
    async def delete_project(
        cls, user_id: UUID, project_id: UUID, access: AccessContext
    ) -> BasicResponse:
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

            if TeamRole.TeamLead not in user_roles and access.role == "user":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only teamlead or admin can delete project",
                )

            teams = await uow.teams.get_by_project(project_id=project_id)

            for team in teams:
                if team.status == UserStatus.Owner or team.status == UserStatus.Member:
                    user = await uow.users.get_by_id(user_id=team.user_id)
                    if user:
                        user.in_team = False

            deleted = await uow.projects.delete(project_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete project",
                )

            await uow.commit()

            return BasicResponse(success=True, message="Project successfully deleted")
