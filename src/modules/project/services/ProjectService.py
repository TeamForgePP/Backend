from datetime import datetime
from typing import TypedDict, cast
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import aliased

from src.core.db.enums import ReportStatus, TeamRole
from src.core.db.models import ProjectReports, ProjectRole, Projects, Reports, Teams, Users
from src.core.db.UnitOfWork import UnitOfWork, get_uow
from src.core.logger import get_logger
from src.core.s3.minio import ALLOWED_MIME, minio_public
from src.core.security.dependencies import PrincipalContext
from src.modules.project.schemas import (
    AllowedActions,
    BasicResponse,
    CreateReportRequest,
    CreateReportResponse,
    EditProjectRequest,
    EditReportRequest,
    EditReportResponse,
    FinalizeReportRequest,
    FinalizeReportResponse,
    FinishProjectRequest,
    PresignedPost,
    ProjectDetailResponse,
    ProjectReport,
    ProjectTeamMember,
    ReportEditInfo,
    ReportUploadInfo,
    TeamExcludeRequest,
)

logger = get_logger("modules.project")

MAX_REPORT_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


class UploadedObjectHead(TypedDict):
    key: str
    size_bytes: int
    content_type: str
    etag: str
    view_url: str


class ProjectService:
    @staticmethod
    def _normalize_content_type(value: str | None) -> str:
        return (value or "").split(";", 1)[0].strip().lower()

    @staticmethod
    def _principal_user_id(principal: PrincipalContext) -> UUID | None:
        if principal.role != "user":
            return None
        try:
            return UUID(principal.sub)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token subject",
            ) from exc

    @staticmethod
    async def _ensure_project_access(
        uow: UnitOfWork,
        *,
        principal: PrincipalContext,
        project: Projects,
    ) -> UUID | None:
        if principal.role == "admin":
            return None

        user_id = ProjectService._principal_user_id(principal)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token subject",
            )

        if user_id == project.teamlead_id or user_id == project.curator_id:
            return user_id

        stmt = select(Teams.id).where(
            Teams.project_id == project.id,
            Teams.user_id == user_id,
        )
        exists = (await uow.session.execute(stmt)).first()
        if exists is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

        return user_id

    @staticmethod
    async def _roles_map_for_project(
        uow: UnitOfWork,
        *,
        project_id: UUID,
    ) -> dict[UUID, list[TeamRole]]:
        stmt = select(ProjectRole.user_id, ProjectRole.role).where(
            ProjectRole.project_id == project_id
        )
        rows = (await uow.session.execute(stmt)).all()

        roles_by_user: dict[UUID, list[TeamRole]] = {}
        for user_id, role in rows:
            roles_by_user.setdefault(user_id, []).append(role)
        return roles_by_user

    @staticmethod
    def _allowed_actions(
        *,
        principal: PrincipalContext,
        project: Projects,
        user_id: UUID | None,
        roles: list[TeamRole],
    ) -> AllowedActions:
        if principal.role == "admin":
            return AllowedActions(can_edit=True, can_finish=True, reports=True)

        is_teamlead = user_id is not None and user_id == project.teamlead_id
        is_curator = user_id is not None and user_id == project.curator_id
        role_set = set(roles)

        can_edit = (
            is_teamlead
            or is_curator
            or TeamRole.TeamLead in role_set
            or TeamRole.Curator in role_set
        )
        can_finish = is_curator or TeamRole.Curator in role_set
        reports = True

        return AllowedActions(can_edit=can_edit, can_finish=can_finish, reports=reports)

    @staticmethod
    async def _project_id_by_report_id(uow: UnitOfWork, *, report_id: UUID) -> UUID:
        stmt = select(ProjectReports.project_id).where(ProjectReports.report_id == report_id)
        project_id = cast(UUID | None, (await uow.session.execute(stmt)).scalar_one_or_none())
        if project_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="report not found")
        return project_id

    @classmethod
    async def get_project(
        cls,
        *,
        principal: PrincipalContext,
    ) -> ProjectDetailResponse:
        async with get_uow() as uow:
            if principal.role == "admin":
                projects = await uow.projects.get_all_uncompleted_projects()
                project = projects[0] if projects else None
            else:
                user_id = cls._principal_user_id(principal)
                if user_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="invalid token subject",
                    )
                project = await uow.projects.get_uncompleted_project_by_user_id(user_id)

            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            user_id = await cls._ensure_project_access(uow, principal=principal, project=project)

            roles_by_user = await cls._roles_map_for_project(uow, project_id=project.id)
            user_roles = roles_by_user.get(user_id, []) if user_id is not None else []
            allowed_actions = cls._allowed_actions(
                principal=principal,
                project=project,
                user_id=user_id,
                roles=user_roles,
            )

            stmt_team = (
                select(Users, Teams)
                .join(Teams, Teams.user_id == Users.id)
                .where(Teams.project_id == project.id)
            )
            team_rows = (await uow.session.execute(stmt_team)).all()

            team: list[ProjectTeamMember] = []
            for user, team_row in team_rows:
                team.append(
                    ProjectTeamMember(
                        id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        roles=roles_by_user.get(user.id, []),
                        status=team_row.status,
                    )
                )

            creator = aliased(Users)
            editor = aliased(Users)
            stmt_reports = (
                select(Reports, creator, editor)
                .join(ProjectReports, ProjectReports.report_id == Reports.id)
                .outerjoin(creator, creator.id == Reports.creator_id)
                .outerjoin(editor, editor.id == Reports.editor_id)
                .where(ProjectReports.project_id == project.id)
                .order_by(Reports.created_at.desc())
            )
            report_rows = (await uow.session.execute(stmt_reports)).all()

            reports: list[ProjectReport] = []
            for report, creator_user, editor_user in report_rows:
                file_key = str(report.id)
                edit_info: ReportEditInfo | None = None
                if report.editor_id and editor_user and report.updated_at:
                    edit_info = ReportEditInfo(
                        editor_id=editor_user.id,
                        editor_fn=editor_user.first_name,
                        editor_ln=editor_user.last_name,
                        updated_at=cast(datetime | None, report.updated_at),
                    )

                reports.append(
                    ProjectReport(
                        id=report.id,
                        file_key=file_key,
                        view_url=minio_public.view_url(file_key),
                        status=report.status,
                        content_type=cls._normalize_content_type(report.content_type),
                        size_bytes=report.size_bytes,
                        creator_id=report.creator_id,
                        creator_fn=creator_user.first_name if creator_user else "",
                        creator_ln=creator_user.last_name if creator_user else "",
                        title=report.title,
                        description=report.description or None,
                        teacher_note=report.teacher_note or None,
                        edit=edit_info,
                    )
                )

            return ProjectDetailResponse(
                project_id=project.id,
                project_name=project.name,
                git=project.github_url,
                description=project.description or "",
                team=team,
                reports=reports,
                allowed_actions=allowed_actions,
            )

    @classmethod
    async def edit_project(
        cls,
        *,
        principal: PrincipalContext,
        data: EditProjectRequest,
    ) -> BasicResponse:
        async with get_uow() as uow:
            project = await uow.projects.get_by_id(data.project_id)
            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            user_id = await cls._ensure_project_access(uow, principal=principal, project=project)
            if principal.role != "admin":
                if user_id not in {project.teamlead_id, project.curator_id}:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

            payload: dict[str, object] = {}
            if data.name is not None:
                payload["name"] = data.name
            if data.github_url is not None:
                payload["github_url"] = data.github_url
            if data.description is not None:
                payload["description"] = data.description

            if payload:
                await uow.projects.update(project.id, payload)

            await uow.commit()
            return BasicResponse(success=True, message="ok")

    @classmethod
    async def create_report(
        cls,
        *,
        principal: PrincipalContext,
        data: CreateReportRequest,
    ) -> CreateReportResponse:
        content_type = cls._normalize_content_type(data.file.content_type)
        size_bytes = int(data.file.size_bytes)

        if size_bytes <= 0 or size_bytes > MAX_REPORT_SIZE_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="FILE_TOO_LARGE")

        if content_type not in ALLOWED_MIME:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID_FILE_TYPE")

        async with get_uow() as uow:
            project = await uow.projects.get_by_id(data.project_id)
            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            user_id = await cls._ensure_project_access(uow, principal=principal, project=project)

            report_id = uuid4()
            file_key = str(report_id)
            view_url = minio_public.view_url(file_key)

            creator_id = user_id if principal.role == "user" else None

            await uow.reports.create(
                {
                    "id": report_id,
                    "file_url": view_url,
                    "content_type": content_type,
                    "size_bytes": size_bytes,
                    "status": ReportStatus.UPLOADING,
                    "creator_id": creator_id,
                    "title": data.title,
                    "description": data.description,
                    "teacher_note": data.teacher_note,
                }
            )
            await uow.project_reports.add_link(project_id=project.id, report_id=report_id)

            try:
                presigned = await minio_public.presign_upload(
                    file_id=report_id,
                    content_type=content_type,
                    size_bytes=size_bytes,
                    max_size_bytes=MAX_REPORT_SIZE_BYTES,
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
                ) from exc

            await uow.commit()

            return CreateReportResponse(
                success=True,
                message="ok",
                report=ReportUploadInfo(
                    id=report_id,
                    file_key=presigned.key,
                    status=ReportStatus.UPLOADING,
                    view_url=view_url,
                    content_type=content_type,
                    size_bytes=size_bytes,
                    upload=PresignedPost(url=presigned.url, fields=presigned.fields),
                ),
            )

    @classmethod
    async def finalize_report(
        cls,
        *,
        principal: PrincipalContext,
        data: FinalizeReportRequest,
    ) -> FinalizeReportResponse:
        report_id = data.report_id
        file_key = str(report_id)

        async with get_uow() as uow:
            report = await uow.reports.get_by_id(report_id)
            if report is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="report not found"
                )

            project_id = await cls._project_id_by_report_id(uow, report_id=report_id)
            project = await uow.projects.get_by_id(project_id)
            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            await cls._ensure_project_access(uow, principal=principal, project=project)

            uploaded: UploadedObjectHead | None
            try:
                uploaded = cast(UploadedObjectHead, await minio_public.head_object(key=file_key))
            except ValueError:
                uploaded = None

            expected_type = cls._normalize_content_type(report.content_type)
            expected_size = int(report.size_bytes or 0)

            if uploaded is None:
                actual_type = ""
                actual_size = 0
            else:
                actual_type = cls._normalize_content_type(uploaded["content_type"])
                actual_size = int(uploaded["size_bytes"])

            ok = (
                uploaded is not None
                and 0 < actual_size <= MAX_REPORT_SIZE_BYTES
                and actual_type in ALLOWED_MIME
                and expected_size > 0
                and expected_type in ALLOWED_MIME
                and actual_size == expected_size
                and actual_type == expected_type
            )

            if not ok:
                try:
                    await minio_public.remove_object(key=file_key)
                except Exception:
                    logger.exception("Failed to remove invalid report object: %s", file_key)

                await uow.reports.delete(report_id)
                await uow.commit()

                return FinalizeReportResponse(
                    success=False,
                    message="INVALID_FILE",
                    report=ReportUploadInfo(
                        id=report_id,
                        file_key=file_key,
                        status=ReportStatus.FAILED,
                        view_url=minio_public.view_url(file_key),
                        content_type=expected_type or None,
                        size_bytes=expected_size or None,
                        upload=None,
                    ),
                )

            assert uploaded is not None
            uploaded_view_url = uploaded["view_url"]
            await uow.reports.update(
                report_id,
                {
                    "status": ReportStatus.READY,
                    "file_url": uploaded_view_url,
                    "content_type": actual_type,
                    "size_bytes": actual_size,
                },
            )
            await uow.commit()

            return FinalizeReportResponse(
                success=True,
                message="ok",
                report=ReportUploadInfo(
                    id=report_id,
                    file_key=file_key,
                    status=ReportStatus.READY,
                    view_url=uploaded_view_url,
                    content_type=actual_type,
                    size_bytes=actual_size,
                    upload=None,
                ),
            )

    @classmethod
    async def delete_report(
        cls,
        *,
        principal: PrincipalContext,
        report_id: UUID,
    ) -> BasicResponse:
        file_key = str(report_id)

        async with get_uow() as uow:
            report = await uow.reports.get_by_id(report_id)
            if report is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="report not found"
                )

            project_id = await cls._project_id_by_report_id(uow, report_id=report_id)
            project = await uow.projects.get_by_id(project_id)
            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            user_id = await cls._ensure_project_access(uow, principal=principal, project=project)

            roles_by_user = await cls._roles_map_for_project(uow, project_id=project.id)
            user_roles = roles_by_user.get(user_id, []) if user_id is not None else []
            allowed = cls._allowed_actions(
                principal=principal,
                project=project,
                user_id=user_id,
                roles=user_roles,
            )

            is_creator = user_id is not None and report.creator_id == user_id
            if not (is_creator or allowed.can_edit):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

            try:
                await minio_public.remove_object(key=file_key)
            except Exception:
                logger.exception("Failed to remove report object: %s", file_key)

            await uow.reports.delete(report_id)
            await uow.commit()

            return BasicResponse(success=True, message="ok")

    @classmethod
    async def edit_report(
        cls,
        *,
        principal: PrincipalContext,
        data: EditReportRequest,
    ) -> EditReportResponse:
        async with get_uow() as uow:
            report = await uow.reports.get_by_id(data.report_id)
            if report is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="report not found"
                )

            project_id = await cls._project_id_by_report_id(uow, report_id=report.id)
            project = await uow.projects.get_by_id(project_id)
            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            user_id = await cls._ensure_project_access(uow, principal=principal, project=project)

            roles_by_user = await cls._roles_map_for_project(uow, project_id=project.id)
            user_roles = roles_by_user.get(user_id, []) if user_id is not None else []
            allowed = cls._allowed_actions(
                principal=principal,
                project=project,
                user_id=user_id,
                roles=user_roles,
            )

            is_creator = user_id is not None and report.creator_id == user_id
            if not (is_creator or allowed.can_edit):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

            editor_id = user_id if principal.role == "user" else None

            await uow.reports.update(
                report.id,
                {
                    "title": data.title,
                    "description": data.description,
                    "teacher_note": data.teacher_note,
                    "editor_id": editor_id,
                },
            )
            updated = await uow.reports.get_by_id(report.id)
            if updated is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="report not found"
                )

            creator_user = (
                await uow.users.get_by_id(updated.creator_id) if updated.creator_id else None
            )
            editor_user = (
                await uow.users.get_by_id(updated.editor_id) if updated.editor_id else None
            )

            edit_info: ReportEditInfo | None = None
            if updated.editor_id and editor_user and updated.updated_at:
                edit_info = ReportEditInfo(
                    editor_id=editor_user.id,
                    editor_fn=editor_user.first_name,
                    editor_ln=editor_user.last_name,
                    updated_at=cast(datetime | None, updated.updated_at),
                )

            await uow.commit()

            file_key = str(updated.id)
            return EditReportResponse(
                success=True,
                message="ok",
                report=ProjectReport(
                    id=updated.id,
                    file_key=file_key,
                    view_url=minio_public.view_url(file_key),
                    status=updated.status,
                    content_type=cls._normalize_content_type(updated.content_type),
                    size_bytes=updated.size_bytes,
                    creator_id=updated.creator_id,
                    creator_fn=creator_user.first_name if creator_user else "",
                    creator_ln=creator_user.last_name if creator_user else "",
                    title=updated.title,
                    description=updated.description,
                    teacher_note=updated.teacher_note,
                    edit=edit_info,
                ),
            )

    @classmethod
    async def exclude_team_member(
        cls,
        *,
        principal: PrincipalContext,
        data: TeamExcludeRequest,
    ) -> BasicResponse:
        async with get_uow() as uow:
            project = await uow.projects.get_by_id(data.project_id)
            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            user_id = await cls._ensure_project_access(uow, principal=principal, project=project)

            roles_by_user = await cls._roles_map_for_project(uow, project_id=project.id)
            user_roles = roles_by_user.get(user_id, []) if user_id is not None else []
            allowed = cls._allowed_actions(
                principal=principal,
                project=project,
                user_id=user_id,
                roles=user_roles,
            )
            if not allowed.can_edit:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

            deleted = await uow.teams.delete_member(project_id=project.id, user_id=data.user_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="team member not found"
                )

            await uow.commit()
            return BasicResponse(success=True, message="ok")

    @classmethod
    async def finish_project(
        cls,
        *,
        principal: PrincipalContext,
        data: FinishProjectRequest,
    ) -> BasicResponse:
        async with get_uow() as uow:
            project = await uow.projects.get_by_id(data.project_id)
            if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
                )

            user_id = await cls._ensure_project_access(uow, principal=principal, project=project)

            roles_by_user = await cls._roles_map_for_project(uow, project_id=project.id)
            user_roles = roles_by_user.get(user_id, []) if user_id is not None else []
            allowed = cls._allowed_actions(
                principal=principal,
                project=project,
                user_id=user_id,
                roles=user_roles,
            )
            if not allowed.can_finish:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

            await uow.projects.update(project.id, {"is_completed": True})
            await uow.commit()

            return BasicResponse(success=True, message="ok")
