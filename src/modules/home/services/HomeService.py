import logging
from datetime import UTC, datetime
from typing import cast
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
    UsersResponse,
)
from src.modules.home.utils.home import HomeUtils
from src.modules.notifications.utils.format import build_notification_content

logger = get_logger("home.service")
logger.setLevel(logging.INFO)


class HomeService:
    @classmethod
    async def create_project(
        cls, data: CreateProjectRequest, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        async with get_uow() as uow:
            try:
                return await cls._create_project_in_uow(uow, data, _user_sub, _user_role)
            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during project creation")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during project creation",
                ) from e

    @staticmethod
    async def _invite_member(
        uow: UnitOfWork,
        *,
        project_id: UUID,
        invited_user_id: UUID,
        invited_by_id: UUID | None,
    ) -> None:
        await uow.teams.create(
            {
                "project_id": project_id,
                "user_id": invited_user_id,
                "status": UserStatus.Invited,
                "created_at": datetime.now(UTC),
            }
        )

        # Для UI: title = имя проекта, message = тип уведомления
        project = await uow.projects.get_by_id(project_id)
        project_name = getattr(project, "name", None) if project else None

        content = build_notification_content(
            NotificationType.NewInvite,
            {"project_name": project_name},
        )

        new_notification = await uow.notifications.create(
            {
                "user_id": invited_user_id,
                "type": NotificationType.NewInvite,
                "title": content.title,
                "message": content.message,
                "project_id": project_id,
                "created_at": datetime.now(UTC),
            }
        )

        await uow.invitations.create(
            {
                "notification_id": new_notification.id,
                "project_id": project_id,
                "invited_user_id": invited_user_id,
                "invited_by_id": invited_by_id,
                "status": InvitationStatus.Posted,
                "created_at": datetime.now(UTC),
            }
        )

    @classmethod
    async def _apply_roles_for_member(
        cls,
        uow: UnitOfWork,
        *,
        project_id: UUID,
        member_id: UUID,
        member_roles: object | None,
        teamlead_id: UUID,
    ) -> None:
        roles_raw: list[object]
        if isinstance(member_roles, list):
            roles_raw = cast(list[object], member_roles)
        else:
            roles_raw = []

        for role in roles_raw:
            role_enum = HomeUtils.as_team_role(role)
            if role_enum == TeamRole.TeamLead and member_id != teamlead_id:
                logger.warning(
                    "Ignoring TeamLead role for non-teamlead member | project_id=%s | user_id=%s",
                    project_id,
                    member_id,
                )
                continue

            await uow.project_roles.add_role(
                project_id=project_id,
                user_id=member_id,
                role=role_enum,
            )

    @classmethod
    async def _create_project_in_uow(
        cls, uow: UnitOfWork, data: CreateProjectRequest, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        logger.info("create_project started | name=%s", getattr(data, "name", None))

        if _user_role == "user":
            teamlead_id = HomeUtils.parse_uuid(_user_sub, detail="Invalid token subject")

            project = await uow.projects.create(
                {
                    "teamlead_id": teamlead_id,
                    "name": data.name,
                    "description": data.description,
                    "github_url": data.github_url,
                    "created_at": datetime.now(UTC),
                }
            )

            await uow.teams.create(
                {
                    "project_id": project.id,
                    "user_id": teamlead_id,
                    "status": UserStatus.Owner,
                    "created_at": datetime.now(UTC),
                }
            )

            await uow.project_roles.add_role(
                project_id=project.id,
                user_id=teamlead_id,
                role=TeamRole.TeamLead,
            )

            for team_member in data.team:
                member_id = getattr(team_member, "id", None)
                if not isinstance(member_id, UUID):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="Invalid team member id format",
                    )

                member_roles = getattr(team_member, "roles", None)

                await cls._apply_roles_for_member(
                    uow,
                    project_id=project.id,
                    member_id=member_id,
                    member_roles=member_roles,
                    teamlead_id=teamlead_id,
                )

                if member_id == teamlead_id:
                    continue

                await cls._invite_member(
                    uow,
                    project_id=project.id,
                    invited_user_id=member_id,
                    invited_by_id=teamlead_id,
                )

            await uow.commit()
            return BasicResponse(success=True, message="Project successfully created")

        if _user_role == "admin":
            team_leads: list[UUID] = []

            for team_member in data.team:
                member_id = getattr(team_member, "id", None)
                if not isinstance(member_id, UUID):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="Invalid team member id format",
                    )

                member_roles = getattr(team_member, "roles", None)
                roles_raw: list[object]
                if isinstance(member_roles, list):
                    roles_raw = cast(list[object], member_roles)
                else:
                    roles_raw = []

                normalized_roles = [HomeUtils.as_team_role(r) for r in roles_raw]
                if TeamRole.TeamLead in normalized_roles:
                    team_leads.append(member_id)

            if len(team_leads) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No team leader in the project",
                )
            if len(team_leads) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only one teamlead can be in project",
                )

            teamlead_id = team_leads[0]

            project = await uow.projects.create(
                {
                    "teamlead_id": teamlead_id,
                    "name": data.name,
                    "description": data.description,
                    "github_url": data.github_url,
                    "created_at": datetime.now(UTC),
                }
            )

            await uow.project_roles.add_role(
                project_id=project.id,
                user_id=teamlead_id,
                role=TeamRole.TeamLead,
            )

            for team_member in data.team:
                member_id = getattr(team_member, "id", None)
                if not isinstance(member_id, UUID):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="Invalid team member id format",
                    )

                member_roles = getattr(team_member, "roles", None)

                await cls._apply_roles_for_member(
                    uow,
                    project_id=project.id,
                    member_id=member_id,
                    member_roles=member_roles,
                    teamlead_id=teamlead_id,
                )

                # В БД invitations.invited_by_id NOT NULL.
                # Админ создаёт проект — считаем, что приглашение “от тимлида проекта”.
                await cls._invite_member(
                    uow,
                    project_id=project.id,
                    invited_user_id=member_id,
                    invited_by_id=teamlead_id,
                )

            await uow.commit()
            return BasicResponse(success=True, message="Project successfully created")

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    @classmethod
    async def get_users_for_team(cls, _user_sub: str, _user_role: Role) -> UsersResponse:
        async with get_uow() as uow:
            try:
                logger.info("get_users_for_team started")

                users: list[object] = []

                if _user_role == "admin":
                    users = cast(list[object], await uow.users.get_all())

                elif _user_role == "user":
                    user_id = HomeUtils.parse_uuid(_user_sub, detail="Invalid token subject")

                    user = await uow.users.get_by_id(user_id)
                    if not user:
                        return UsersResponse(users=[])

                    group_id = getattr(user, "group_id", None)
                    if not isinstance(group_id, UUID):
                        return UsersResponse(users=[])

                    users = cast(list[object], await uow.users.get_by_group(group_id))

                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unauthorized user",
                    )

                return HomeUtils.to_users_response(users)

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get users")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get users",
                ) from e

    @classmethod
    async def get_home_info(cls, _user_sub: str, _user_role: Role) -> ProjectsResponse:
        async with get_uow() as uow:
            try:
                if _user_role == "user":
                    user_id = HomeUtils.parse_uuid(_user_sub, detail="Invalid token subject")

                    projects_raw = await uow.projects.get_projects_id_by_user_id(user_id)
                    if not projects_raw:
                        return ProjectsResponse(projects=[])

                    projects: list[object] = []
                    for item in projects_raw:
                        if isinstance(item, UUID):
                            p = await uow.projects.get_by_id(item)
                            if p is not None:
                                projects.append(p)
                        else:
                            projects.append(item)

                    if not projects:
                        return ProjectsResponse(projects=[])

                    projects_response: list[Project] = []

                    for project in projects:
                        project_id = getattr(project, "id", None)
                        if not isinstance(project_id, UUID):
                            raise RuntimeError("Invalid project id type in repository result")

                        roles = await uow.project_roles.get_roles_for_user_in_project(
                            project_id, user_id
                        )
                        roles = roles or []

                        sprints = await uow.sprints.get_by_project_id(project_id)
                        sprints = sprints or []

                        sprints_map_user: list[SprintMap] = []
                        current_sprints_user: list[SprintMap] = []

                        for sprint in sprints:
                            sprint_id = getattr(sprint, "id", None)
                            if not isinstance(sprint_id, UUID):
                                continue

                            sprint_name = HomeUtils.as_str(getattr(sprint, "name", ""))

                            sprint_seq_raw = getattr(sprint, "seq", 0)
                            if isinstance(sprint_seq_raw, int):
                                sprint_seq = sprint_seq_raw
                            else:
                                try:
                                    sprint_seq = int(sprint_seq_raw)
                                except Exception:
                                    sprint_seq = 0

                            sprint_deadline = HomeUtils.as_date(getattr(sprint, "deadline", None))
                            is_active = HomeUtils.is_active_sprint(getattr(sprint, "status", None))

                            if is_active:
                                m = SprintMap(
                                    id=sprint_id,
                                    name=sprint_name,
                                    seq=sprint_seq,
                                    active=True,
                                    deadline=sprint_deadline,
                                )
                                sprints_map_user.append(m)
                                current_sprints_user.append(m)
                            else:
                                sprints_map_user.append(
                                    SprintMap(
                                        id=sprint_id,
                                        name=sprint_name,
                                        seq=sprint_seq,
                                        deadline=sprint_deadline,
                                    )
                                )

                        if current_sprints_user:
                            current_sprint = min(current_sprints_user, key=lambda s: s.seq)
                            current_sprint_seq = current_sprint.seq
                            current_sprint_name = current_sprint.name
                        else:
                            current_sprint_seq = 0
                            current_sprint_name = ""

                        tasks = await uow.tasks.get_by_project(project_id)
                        tasks = tasks or []

                        deadlines_raw_user: list[object] = []
                        for task in tasks:
                            task_id = getattr(task, "id", None)
                            if not isinstance(task_id, UUID):
                                continue

                            assignees = await uow.performes.get_assignee_ids_by_task(task_id)
                            assignees = assignees or []
                            if user_id in assignees:
                                deadlines_raw_user.append(getattr(task, "deadline", None))

                        deadlines_user = HomeUtils.safe_deadline_list(deadlines_raw_user)
                        nearest_deadline_user = min(deadlines_user) if deadlines_user else None

                        is_owner = TeamRole.TeamLead in roles
                        allowed_actions = AllowedActions(
                            can_delete=is_owner,
                            can_leave=not is_owner,
                        )

                        project_name = HomeUtils.as_str(getattr(project, "name", ""))

                        project_info = Project(
                            id=project_id,
                            name=project_name,
                            is_completed=HomeUtils.as_bool(getattr(project, "is_completed", False)),
                            current_sprint_name=current_sprint_name,
                            current_sprint_seq=int(current_sprint_seq),
                            role=roles,
                            nearest_deadline=nearest_deadline_user,
                            sprint_map=sprints_map_user,
                            allowed_actions=allowed_actions,
                        )

                        projects_response.append(project_info)

                    return ProjectsResponse(projects=projects_response)

                if _user_role == "admin":
                    projects_admin = await uow.projects.get_all_uncompleted_projects()
                    if not projects_admin:
                        return ProjectsResponse(projects=[])

                    admin_projects_response: list[Project] = []

                    for project_admin in projects_admin:
                        project_id_admin = getattr(project_admin, "id", None)
                        if not isinstance(project_id_admin, UUID):
                            raise RuntimeError("Invalid project id type in repository result")

                        sprints_admin = await uow.sprints.get_by_project_id(project_id_admin)
                        sprints_admin = sprints_admin or []

                        sprints_map_admin: list[SprintMap] = []
                        current_sprints_admin: list[SprintMap] = []

                        for sprint_admin in sprints_admin:
                            sprint_id_admin = getattr(sprint_admin, "id", None)
                            if not isinstance(sprint_id_admin, UUID):
                                continue

                            sprint_name_admin = HomeUtils.as_str(getattr(sprint_admin, "name", ""))

                            sprint_seq_raw_admin = getattr(sprint_admin, "seq", 0)
                            if isinstance(sprint_seq_raw_admin, int):
                                sprint_seq_admin = sprint_seq_raw_admin
                            else:
                                try:
                                    sprint_seq_admin = int(sprint_seq_raw_admin)
                                except Exception:
                                    sprint_seq_admin = 0

                            sprint_deadline_admin = HomeUtils.as_date(
                                getattr(sprint_admin, "deadline", None)
                            )
                            is_active_admin = HomeUtils.is_active_sprint(
                                getattr(sprint_admin, "status", None)
                            )

                            if is_active_admin:
                                m_admin = SprintMap(
                                    id=sprint_id_admin,
                                    name=sprint_name_admin,
                                    seq=sprint_seq_admin,
                                    active=True,
                                    deadline=sprint_deadline_admin,
                                )
                                sprints_map_admin.append(m_admin)
                                current_sprints_admin.append(m_admin)
                            else:
                                sprints_map_admin.append(
                                    SprintMap(
                                        id=sprint_id_admin,
                                        name=sprint_name_admin,
                                        seq=sprint_seq_admin,
                                        deadline=sprint_deadline_admin,
                                    )
                                )

                        if current_sprints_admin:
                            current_sprint_admin = min(current_sprints_admin, key=lambda s: s.seq)
                            current_sprint_seq_admin = current_sprint_admin.seq
                            current_sprint_name_admin = current_sprint_admin.name
                        else:
                            current_sprint_seq_admin = 0
                            current_sprint_name_admin = ""

                        tasks_admin = await uow.tasks.get_by_project(project_id_admin)
                        tasks_admin = tasks_admin or []

                        deadlines_raw_admin: list[object] = []
                        for task_admin in tasks_admin:
                            deadlines_raw_admin.append(getattr(task_admin, "deadline", None))

                        deadlines_admin = HomeUtils.safe_deadline_list(deadlines_raw_admin)
                        nearest_deadline_admin = min(deadlines_admin) if deadlines_admin else None

                        allowed_actions_admin = AllowedActions(
                            can_delete=True,
                            can_leave=False,
                        )

                        project_name_admin = HomeUtils.as_str(getattr(project_admin, "name", ""))

                        project_info_admin = Project(
                            id=project_id_admin,
                            name=project_name_admin,
                            is_completed=False,
                            current_sprint_name=current_sprint_name_admin,
                            current_sprint_seq=int(current_sprint_seq_admin),
                            role=[],
                            nearest_deadline=nearest_deadline_admin,
                            sprint_map=sprints_map_admin,
                            allowed_actions=allowed_actions_admin,
                        )

                        admin_projects_response.append(project_info_admin)

                    return ProjectsResponse(projects=admin_projects_response)

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get info")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    @classmethod
    async def leave_project(cls, user_id: UUID, project_id: UUID) -> BasicResponse:
        async with get_uow() as uow:
            logger.info("leave_project started | project_id=%s", project_id)

            project = await uow.projects.get_by_id(project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )

            if getattr(project, "teamlead_id", None) == user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Teamlead can't leave project"
                )

            roles = await uow.project_roles.get_roles_for_user_in_project(
                project_id=project_id, user_id=user_id
            )
            if not roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="You're not a project member"
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

    @classmethod
    async def delete_project(
        cls, _user_sub: str, _user_role: Role, project_id: UUID
    ) -> BasicResponse:
        async with get_uow() as uow:
            logger.info("delete_project started | project_id=%s", project_id)

            project = await uow.projects.get_by_id(project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or already deleted",
                )

            if _user_role == "user":
                user_id = HomeUtils.parse_uuid(_user_sub, detail="Invalid token subject")

                user_roles = await uow.project_roles.get_roles_for_user_in_project(
                    project_id=project_id, user_id=user_id
                )
                user_roles = user_roles or []

                if TeamRole.TeamLead not in user_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Only teamlead or admin can delete project",
                    )

                deleted = await uow.projects.delete(project_id)
                if not deleted:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project not found or already deleted",
                    )

                await uow.commit()
                return BasicResponse(success=True, message="Project successfully deleted")

            if _user_role == "admin":
                deleted = await uow.projects.delete(project_id)
                if not deleted:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project not found or already deleted",
                    )

                await uow.commit()
                return BasicResponse(success=True, message="Project successfully deleted")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized user",
            )
