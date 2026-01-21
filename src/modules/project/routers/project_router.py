from uuid import UUID

from fastapi import APIRouter, status

from src.core.security.dependencies import PrincipalContext, principal_context_dep
from src.modules.project.schemas import (
    BasicResponse,
    CreateReportRequest,
    CreateReportResponse,
    EditProjectRequest,
    EditReportRequest,
    EditReportResponse,
    FinalizeReportRequest,
    FinalizeReportResponse,
    FinishProjectRequest,
    ProjectDetailResponse,
    TeamExcludeRequest,
)
from src.modules.project.services.ProjectService import ProjectService

router = APIRouter(prefix="/project", tags=["project"])


@router.get(
    "",
    response_model=ProjectDetailResponse,
)
async def get_project(
    principal: PrincipalContext = principal_context_dep,
) -> ProjectDetailResponse:
    return await ProjectService.get_project(
        principal=principal,
    )


@router.post(
    "/edit",
    response_model=BasicResponse,
)
async def edit_project(
    body: EditProjectRequest,
    principal: PrincipalContext = principal_context_dep,
) -> BasicResponse:
    return await ProjectService.edit_project(principal=principal, data=body)


@router.post(
    "/report",
    response_model=CreateReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_report(
    body: CreateReportRequest,
    principal: PrincipalContext = principal_context_dep,
) -> CreateReportResponse:
    return await ProjectService.create_report(
        principal=principal,
        data=body,
    )


@router.post(
    "/report/finalize",
    response_model=FinalizeReportResponse,
)
async def finalize_report(
    body: FinalizeReportRequest,
    principal: PrincipalContext = principal_context_dep,
) -> FinalizeReportResponse:
    return await ProjectService.finalize_report(principal=principal, data=body)


@router.delete(
    "/report/{report_id}",
    response_model=BasicResponse,
)
async def delete_report(
    report_id: UUID,
    principal: PrincipalContext = principal_context_dep,
) -> BasicResponse:
    return await ProjectService.delete_report(principal=principal, report_id=report_id)


@router.post(
    "/report/edit",
    response_model=EditReportResponse,
)
async def edit_report(
    body: EditReportRequest,
    principal: PrincipalContext = principal_context_dep,
) -> EditReportResponse:
    return await ProjectService.edit_report(
        principal=principal,
        data=body,
    )


@router.post(
    "/team/exclude",
    response_model=BasicResponse,
)
async def exclude_team_member(
    body: TeamExcludeRequest,
    principal: PrincipalContext = principal_context_dep,
) -> BasicResponse:
    return await ProjectService.exclude_team_member(principal=principal, data=body)


@router.post(
    "/finish",
    response_model=BasicResponse,
)
async def finish_project(
    body: FinishProjectRequest,
    principal: PrincipalContext = principal_context_dep,
) -> BasicResponse:
    return await ProjectService.finish_project(principal=principal, data=body)
