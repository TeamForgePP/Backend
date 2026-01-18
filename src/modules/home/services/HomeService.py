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
from src.core.security.dependencies import Role
from src.modules.home.schemas import (
    AllowedActions,
    BasicResponse,
    CreateProjectRequest,
    Project,
    ProjectsResponse,
    SprintMap,
    User,
    UsersResponse,
)

logger = get_logger("home.service")
logger.setLevel(logging.INFO)


class HomeService:
    # ---------------- CREATE ---------------- #

    @classmethod
    async def create_project(
        cls, data: CreateProjectRequest, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        async with get_uow() as uow:
            try:
                return await cls._create_project_in_uow(uow, data, _user_sub, _user_role)
            except Exception as e:
                logger.error("Error during project creation: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during project creation",
                ) from e

    @classmethod
    async def _create_project_in_uow(
        cls, uow: UnitOfWork, data: CreateProjectRequest, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        logger.info("create_project started | name=%s", data.name)

        if _user_role == "user":
            user_id = UUID(_user_sub)
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

        elif _user_role == "admin":
            team_leads = []

            for team_member in data.team:
                if team_member.roles and TeamRole.TeamLead in team_member.roles:
                    team_leads.append(team_member.id)

            if len(team_leads) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="No team leader in the project"
                )
            elif len(team_leads) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only one teamlead can be in project",
                )

            team_lead = team_leads[0]

            project = await uow.projects.create(
                {
                    "teamlead_id": team_lead,
                    "name": data.name,
                    "description": data.description,
                    "git_organization": data.git_organization,
                    "created_at": datetime.now(UTC),
                }
            )

            for team_member in data.team:
                if team_member.roles:
                    for role in team_member.roles:
                        if role not in TeamRole:
                            raise HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail="Invalid team role format",
                            )

                        elif role == TeamRole.TeamLead and team_member.id != team_lead:
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
                        "invited_by_id": None,
                        "status": InvitationStatus.Posted,
                        "created_at": datetime.now(UTC),
                    }
                )
            await uow.commit()
            return BasicResponse(success=True, message="Project successfully created")

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
            )

    # ---------------- GET ---------------- #

    @classmethod
    async def get_users_for_team(cls, _user_sub: str, _user_role: Role) -> UsersResponse:
        async with get_uow() as uow:
            try:
                logger.info("get_users_for_team started")

                if _user_role == "user":
                    user_id = UUID(_user_sub)
                    user = await uow.users.get_by_id(user_id)
                    if not user:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                        )
                    if not user.group_id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User doesn't belong to any group",
                        )

                    users = await uow.users.get_by_group(user.group_id)
                    if not users:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Users not found"
                        )
                    users_response_for_admin: list[User] = []

                    for u in users:
                        info = User(
                            id=u.id, name=u.first_name, last_name=u.last_name, in_team=u.in_team
                        )
                        users_response_for_admin.append(info)
                    return UsersResponse(users=users_response_for_admin)

                elif _user_role == "admin":
                    users = await uow.users.get_all()
                    users_response: list[User] = []

                    for u in users:
                        info = User(
                            id=u.id, name=u.first_name, last_name=u.last_name, in_team=u.in_team
                        )
                        users_response.append(info)
                    return UsersResponse(users=users_response)

                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
                    )

            except HTTPException:
                raise
            except Exception as e:
                logger.error("Error during get users: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get users",
                ) from e

    @classmethod
    async def get_home_info(cls, _user_sub: str, _user_role: Role) -> ProjectsResponse:
        async with get_uow() as uow:
            try:
                logger.info("get_home_info started")

                if _user_role == "user":
                    user_id = UUID(_user_sub)

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
                            can_delete=((TeamRole.TeamLead in roles) or (_user_role == "admin")),
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

                elif _user_role == "admin":
                    projects = await uow.projects.get_all_uncompleted_projects()

                    if not projects:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                        )

                    admin_projects_response: list[Project] = []

                    for project in projects:
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
                            deadlines.append(task.deadline)

                        if deadlines:
                            nearest_deadline = min(deadlines)  # type: ignore
                        else:
                            nearest_deadline = None

                        allowed_actions = AllowedActions(
                            can_delete=(_user_role == "admin"),
                            can_leave=False,
                        )

                        project_info = Project(
                            id=project.id,
                            name=project.name,
                            is_completed=False,
                            current_sprint_name=current_sprint_name,
                            current_sprint_seq=current_sprint_seq,
                            role=[],
                            nearest_deadline=nearest_deadline,  # type:ignore
                            sprint_map=sprints_map,
                            allowed_actions=allowed_actions,
                        )

                        admin_projects_response.append(project_info)

                    return ProjectsResponse(projects=admin_projects_response)

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
        cls, _user_sub: str, _user_role: Role, project_id: UUID
    ) -> BasicResponse:
        async with get_uow() as uow:
            logger.info("delete_project started | project_id=%s", project_id)

            exists = await uow.projects.get_by_id(project_id)
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or already deleted",
                )
            if _user_role == "user":
                user_id = UUID(_user_sub)
                user_roles = await uow.project_roles.get_roles_for_user_in_project(
                    project_id=project_id, user_id=user_id
                )

                if TeamRole.TeamLead not in user_roles:
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

            elif _user_role == "admin":
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

            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
                )
