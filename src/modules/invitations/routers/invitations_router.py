from uuid import UUID

from fastapi import APIRouter, Depends

from src.core.db import UnitOfWork, get_uow
from src.core.security.dependencies import PrincipalContext, principal_context_dep
from src.modules.invitations.schemas.invitations import (
    AcceptedDeadlineResponse,
    BasicResponse,
    InvitationInfoResponse,
)
from src.modules.invitations.services.InvitationsService import InvitationsService

router = APIRouter(prefix="/user/invitations", tags=["Invitations"])
uow_dep = Depends(get_uow)


@router.get(
    "/{invitation_id}",
    response_model=InvitationInfoResponse,
)
async def get_invitation_info(
    invitation_id: UUID,
    principal: PrincipalContext = principal_context_dep,
    uow: UnitOfWork = uow_dep,
) -> dict:
    service = InvitationsService(uow=uow, principal=principal)
    return await service.get_invitation_info(invitation_id)


@router.post(
    "/{invitation_id}/accept",
    response_model=BasicResponse,
)
async def accept(
    invitation_id: UUID,
    principal: PrincipalContext = principal_context_dep,
    uow: UnitOfWork = uow_dep,
) -> dict:
    service = InvitationsService(uow=uow, principal=principal)
    return await service.accept(invitation_id)


@router.post(
    "/{invitation_id}/decline",
    response_model=BasicResponse,
)
async def decline(
    invitation_id: UUID,
    principal: PrincipalContext = principal_context_dep,
    uow: UnitOfWork = uow_dep,
) -> dict:
    service = InvitationsService(uow=uow, principal=principal)
    return await service.decline(invitation_id)


@router.get(
    "/{invitation_id}/accepted-deadline",
    response_model=AcceptedDeadlineResponse,
)
async def accepted_deadline(
    invitation_id: UUID,
    principal: PrincipalContext = principal_context_dep,
    uow: UnitOfWork = uow_dep,
) -> dict:
    service = InvitationsService(uow=uow, principal=principal)
    return await service.accepted_deadline(invitation_id)
