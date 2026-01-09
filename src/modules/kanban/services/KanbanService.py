import logging
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import NotificationType, TaskStatus, TeamRole, UnitOfWork, get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import Role
from src.modules.kanban.schemas import (
    BasicResponse,
    KanbanResponse,
    MembersResponse,
    NewTaskRequest,
    Performer,
    Project,
    SelectedSprint,
    Task,
    TaskResponse,
    UpdateStatusRequest,
)

logger = get_logger("home.service")
logger.setLevel(logging.INFO)


class KanbanService:
    # ---------------- GET ---------------- #

    @classmethod
    async def get_kanban_info(cls, _user_sub: str, _user_role: Role) -> KanbanResponse:
        async with get_uow() as uow:
            try:
                if _user_role == "user":
                    user_id = UUID(_user_sub)
                    project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
                    if not project:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                        )

                    project_response = Project(id=project.id, name=project.name)

                    sprints = await uow.sprints.get_by_project_id(project.id)
                    current_sprints = []
                    for sprint in sprints:
                        if sprint.status == "active":
                            current_sprints.append(
                                SelectedSprint(
                                    id=sprint.id,
                                    seq=sprint.seq,
                                )
                            )
                    if current_sprints:
                        current_sprint = min(current_sprints, key=lambda s: s.seq)
                        current_sprint_id = current_sprint.id
                        current_sprint_seq = current_sprint.seq
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Sprints not found"
                        )

                    sprint_response = SelectedSprint(id=current_sprint_id, seq=current_sprint_seq)

                    tasks = await uow.tasks.get_by_sprint_id(current_sprint_id)

                    if not tasks:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
                        )

                    tasks_response: list[Task] = []
                    for task in tasks:
                        assignee_ids = await uow.performes.get_assignee_ids_by_task(task.id)
                        performes: list[Performer] = []
                        all_roles: list[TeamRole] = []
                        for assignee_id in assignee_ids:
                            user = await uow.users.get_by_id(assignee_id)
                            if not user:
                                raise HTTPException(
                                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                                )
                            performes.append(
                                Performer(
                                    id=assignee_id,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    avatar_url=user.avatar_url or "",
                                )
                            )
                            roles = await uow.project_roles.get_roles_for_user_in_project(
                                project.id, assignee_id
                            )
                            for role in roles:
                                if role not in all_roles:
                                    all_roles.append(role)

                        task_info = Task(
                            id=task.id,
                            title=task.title,
                            tags=all_roles,
                            status=task.status,
                            deadline=task.deadline,  # type: ignore
                            priority=task.priority,
                            performes=performes,
                            key=task.key,
                        )
                        tasks_response.append(task_info)

                    kanban_response = KanbanResponse(
                        project=project_response,
                        selected_sprint=sprint_response,
                        tasks=tasks_response,
                    )
                    return kanban_response

                elif _user_role == "admin":
                    projects = await uow.projects.get_all_uncompleted_projects()
                    if not projects:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                        )

                    project = projects[0]  # пусть админу пока выводится рандомный проект
                    project_response = Project(id=project.id, name=project.name)

                    sprints = await uow.sprints.get_by_project_id(project.id)
                    current_sprints = []
                    for sprint in sprints:
                        if sprint.status == "active":
                            current_sprints.append(
                                SelectedSprint(
                                    id=sprint.id,
                                    seq=sprint.seq,
                                )
                            )
                    if current_sprints:
                        current_sprint = min(current_sprints, key=lambda s: s.seq)
                        current_sprint_id = current_sprint.id
                        current_sprint_seq = current_sprint.seq
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Sprints not found"
                        )

                    sprint_response = SelectedSprint(id=current_sprint_id, seq=current_sprint_seq)

                    tasks = await uow.tasks.get_by_sprint_id(current_sprint_id)

                    if not tasks:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
                        )

                    tasks_response: list[Task] = []
                    for task in tasks:
                        assignee_ids = await uow.performes.get_assignee_ids_by_task(task.id)
                        performes: list[Performer] = []
                        all_roles: list[TeamRole] = []
                        for assignee_id in assignee_ids:
                            user = await uow.users.get_by_id(assignee_id)
                            if not user:
                                raise HTTPException(
                                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                                )
                            performes.append(
                                Performer(
                                    id=assignee_id,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    avatar_url=user.avatar_url or "",
                                )
                            )
                            roles = await uow.project_roles.get_roles_for_user_in_project(
                                project.id, assignee_id
                            )
                            for role in roles:
                                if role not in all_roles:
                                    all_roles.append(role)

                        task_info = Task(
                            id=task.id,
                            title=task.title,
                            tags=all_roles,
                            status=task.status,
                            deadline=task.deadline,  # type: ignore
                            priority=task.priority,
                            performes=performes,
                            key=task.key,
                        )
                        tasks_response.append(task_info)

                    kanban_response = KanbanResponse(
                        project=project_response,
                        selected_sprint=sprint_response,
                        tasks=tasks_response,
                    )
                    return kanban_response

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
    async def get_kanban_info_by_sprint_id(
        cls, _user_sub: str, _user_role: Role, sprint_id: UUID
    ) -> KanbanResponse:
        async with get_uow() as uow:
            try:
                if _user_role == "user":
                    user_id = UUID(_user_sub)
                    project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
                    if not project:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                        )

                    project_response = Project(id=project.id, name=project.name)

                    sprint = await uow.sprints.get_by_id(sprint_id)
                    if not sprint:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
                        )

                    sprint_response = SelectedSprint(id=sprint_id, seq=sprint.seq)

                    tasks = await uow.tasks.get_by_sprint_id(sprint_id)

                    if not tasks:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
                        )

                    tasks_response: list[Task] = []
                    for task in tasks:
                        assignee_ids = await uow.performes.get_assignee_ids_by_task(task.id)
                        performes: list[Performer] = []
                        all_roles: list[TeamRole] = []
                        for assignee_id in assignee_ids:
                            user = await uow.users.get_by_id(assignee_id)
                            if not user:
                                raise HTTPException(
                                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                                )
                            performes.append(
                                Performer(
                                    id=assignee_id,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    avatar_url=user.avatar_url or "",
                                )
                            )
                            roles = await uow.project_roles.get_roles_for_user_in_project(
                                project.id, assignee_id
                            )
                            for role in roles:
                                if role not in all_roles:
                                    all_roles.append(role)

                        task_info = Task(
                            id=task.id,
                            title=task.title,
                            tags=all_roles,
                            status=task.status,
                            deadline=task.deadline,  # type: ignore
                            priority=task.priority,
                            performes=performes,
                            key=task.key,
                        )
                        tasks_response.append(task_info)

                    kanban_response = KanbanResponse(
                        project=project_response,
                        selected_sprint=sprint_response,
                        tasks=tasks_response,
                    )
                    return kanban_response

                elif _user_role == "admin":
                    projects = await uow.projects.get_all_uncompleted_projects()
                    if not projects:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                        )

                    project = projects[0]  # пусть админу пока выводится рандомный проект
                    project_response = Project(id=project.id, name=project.name)

                    sprint = await uow.sprints.get_by_id(sprint_id)
                    if not sprint:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
                        )

                    sprint_response = SelectedSprint(id=sprint_id, seq=sprint.seq)

                    tasks = await uow.tasks.get_by_sprint_id(sprint_id)

                    if not tasks:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
                        )

                    tasks_response: list[Task] = []
                    for task in tasks:
                        assignee_ids = await uow.performes.get_assignee_ids_by_task(task.id)
                        performes: list[Performer] = []
                        all_roles: list[TeamRole] = []
                        for assignee_id in assignee_ids:
                            user = await uow.users.get_by_id(assignee_id)
                            if not user:
                                raise HTTPException(
                                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                                )
                            performes.append(
                                Performer(
                                    id=assignee_id,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    avatar_url=user.avatar_url or "",
                                )
                            )
                            roles = await uow.project_roles.get_roles_for_user_in_project(
                                project.id, assignee_id
                            )
                            for role in roles:
                                if role not in all_roles:
                                    all_roles.append(role)

                        task_info = Task(
                            id=task.id,
                            title=task.title,
                            tags=all_roles,
                            status=task.status,
                            deadline=task.deadline,  # type: ignore
                            priority=task.priority,
                            performes=performes,
                            key=task.key,
                        )
                        tasks_response.append(task_info)

                    kanban_response = KanbanResponse(
                        project=project_response,
                        selected_sprint=sprint_response,
                        tasks=tasks_response,
                    )
                    return kanban_response

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
    async def get_all_team_members(cls, _user_sub: str, _user_role: Role) -> MembersResponse:
        async with get_uow() as uow:
            try:
                if _user_role == "user":
                    user_id = UUID(_user_sub)
                    project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
                    if not project:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                        )

                    members = await uow.teams.get_by_project(project.id)

                    members_info: list[Performer] = []
                    for member in members:
                        user = await uow.users.get_by_id(member.user_id)
                        if not user:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                            )
                        info = Performer(
                            id=member.user_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            avatar_url=user.avatar_url or "",
                        )
                        members_info.append(info)

                    return MembersResponse(members=members_info)

                elif _user_role == "admin":
                    projects = await uow.projects.get_all_uncompleted_projects()
                    if not projects:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                        )
                    project = projects[0]  # пусть админу пока выводится рандомный проект

                    members = await uow.teams.get_by_project(project.id)

                    members_info: list[Performer] = []
                    for member in members:
                        user = await uow.users.get_by_id(member.user_id)
                        if not user:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                            )
                        info = Performer(
                            id=member.user_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            avatar_url=user.avatar_url or "",
                        )
                        members_info.append(info)

                    return MembersResponse(members=members_info)

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
    async def get_task(cls, task_id: UUID) -> TaskResponse:
        async with get_uow() as uow:
            try:
                task = await uow.tasks.get_by_id(task_id)
                if not task:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
                    )

                assignee_ids = await uow.performes.get_assignee_ids_by_task(task_id)
                users_response: list[Performer] = []
                for assignee_id in assignee_ids:
                    user = await uow.users.get_by_id(assignee_id)
                    if not user:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                        )
                    info = Performer(
                        id=assignee_id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        avatar_url=user.avatar_url or "",
                    )
                    users_response.append(info)

                task_response = TaskResponse(
                    id=task_id,
                    title=task.title,
                    description=task.description or "",
                    users=users_response,
                    priority=task.priority,
                    deadline=task.deadline,  # type: ignore
                )

                return task_response

            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    # ---------------- CREATE ---------------- #
    @classmethod
    async def create_task(
        cls, data: NewTaskRequest, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        async with get_uow() as uow:
            try:
                return await cls._create_task_in_uow(uow, data, _user_sub, _user_role)
            except Exception as e:
                logger.error("Error during task creation: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during task creation",
                ) from e

    @classmethod
    async def _create_task_in_uow(
        cls, uow: UnitOfWork, data: NewTaskRequest, _user_sub: str, _user_role: Role
    ) -> BasicResponse:
        logger.info("create_task started")

        if _user_role == "user":
            user_id = UUID(_user_sub)
            project = await uow.projects.get_uncompleted_project_by_user_id(user_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )

            all_roles: list[TeamRole] = []
            for performer in data.performes:
                roles = await uow.project_roles.get_roles_for_user_in_project(
                    project.id, performer.id
                )
                for role in roles:
                    if role not in all_roles:
                        all_roles.append(role)

            if data.sprint_id:
                sprint = await uow.sprints.get_by_id(data.sprint_id)
                if not sprint:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found in project"
                    )

                if sprint.project_id != project.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Sprint doesn't belong to project",
                    )

            else:
                sprint = await uow.sprints.get_active_sprint_in_project(project.id)
                if not sprint:
                    sprints = await uow.sprints.get_future_sprints_in_project(project.id)
                    if not sprints:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Sprints not exist"
                        )
                    sprint = sprints[0]

                data.sprint_id = sprint.id

            task = await uow.tasks.create(
                {
                    "project_id": project.id,
                    "sprint_id": data.sprint_id,
                    "title": data.title,
                    "description": data.description,
                    "priority": data.priority,
                    "tag": all_roles,
                    "status": TaskStatus.ToDo,
                    "deadline": data.deadline,
                }
            )

            for performer in data.performes:
                await uow.performes.add(task.id, performer.id)
                await uow.notifications.create(
                    {
                        "user_id": performer.id,
                        "type": NotificationType.NewTask,
                        "title": "You have a new task",  # я хз конечно можно ли так делать
                        "message": data.title,
                        "project_id": project.id,
                        "is_read": False,
                    }
                )

            await uow.commit()
            return BasicResponse(success=True, message="Task successfully created")

        elif _user_role == "admin":
            projects = await uow.projects.get_all_uncompleted_projects()
            if not projects:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found"
                )
            project = projects[0]

            all_roles: list[TeamRole] = []
            for performer in data.performes:
                roles = await uow.project_roles.get_roles_for_user_in_project(
                    project.id, performer.id
                )
                for role in roles:
                    if role not in all_roles:
                        all_roles.append(role)

            if data.sprint_id:
                sprint = await uow.sprints.get_by_id(data.sprint_id)
                if not sprint:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found in project"
                    )

                if sprint.project_id != project.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Sprint doesn't belong to project",
                    )

            else:
                sprint = await uow.sprints.get_active_sprint_in_project(project.id)
                if not sprint:
                    sprints = await uow.sprints.get_future_sprints_in_project(project.id)
                    if not sprints:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Sprints not exist"
                        )
                    sprint = sprints[0]

                data.sprint_id = sprint.id

            task = await uow.tasks.create(
                {
                    "project_id": project.id,
                    "sprint_id": data.sprint_id,
                    "title": data.title,
                    "description": data.description,
                    "priority": data.priority,
                    "tag": all_roles,
                    "status": TaskStatus.ToDo,
                    "deadline": data.deadline,
                }
            )

            for performer in data.performes:
                await uow.performes.add(task.id, performer.id)
                await uow.notifications.create(
                    {
                        "user_id": performer.id,
                        "type": NotificationType.NewTask,
                        "title": "You have a new task",
                        "message": data.title,
                        "project_id": project.id,
                        "is_read": False,
                    }
                )

            await uow.commit()
            return BasicResponse(success=True, message="Task successfully created")

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
            )

    # ---------------- POST ---------------- #

    @classmethod
    async def update_status(cls, data: UpdateStatusRequest) -> BasicResponse:
        async with get_uow() as uow:
            try:
                await uow.tasks.update(data.task_id, {"status": data.status})
                await uow.commit()

                return BasicResponse(success=True, message="Task status updated successfully")

            except Exception as e:
                logger.error("Error during update status: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during update status",
                ) from e
