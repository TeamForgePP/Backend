import logging
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import (
    InvitationStatus,
    UserStatus,
    get_uow,
)
from src.core.logger import get_logger
from src.modules.notifications.shemas import (
    BasicResponse,
    InvitationResponse,
    Participant,
    Project,
    TeamLeader,
)
from src.modules.notifications.utils import InvitationUtils

logger = get_logger("invitations.service")
logger.setLevel(logging.INFO)


class InvitationsService:
    @classmethod
    async def get_invitation_info(
        cls,
        notification_id: UUID,
        user_id: UUID,
    ) -> InvitationResponse:
        async with get_uow() as uow:
            try:
                ctx = await InvitationUtils.load_invitation_context(uow, notification_id, user_id)
                notification = ctx.notification
                invitation = ctx.invitation

                project = await uow.projects.get_by_id(project_id=invitation.project_id)
                if not project:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project not found",
                    )

                teamlead = await uow.users.get_by_id(user_id=project.teamlead_id)
                if not teamlead:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Teamlead not found",
                    )

                roles_teamlead = (
                    await uow.project_roles.get_roles_for_user_in_project(
                        project_id=project.id,
                        user_id=teamlead.id,
                    )
                    or []
                )

                info_teamlead = TeamLeader(
                    id=teamlead.id,
                    first_name=teamlead.first_name,
                    last_name=teamlead.last_name,
                    roles=roles_teamlead,
                )

                team_rows = await uow.teams.get_by_project(project_id=project.id)
                allowed_user_ids = [
                    t.user_id
                    for t in team_rows
                    if t.status in (UserStatus.Owner, UserStatus.Member)
                ]

                participants: list[Participant] = []
                for uid in allowed_user_ids:
                    participant = await uow.users.get_by_id(user_id=uid)
                    if not participant:
                        continue

                    roles = (
                        await uow.project_roles.get_roles_for_user_in_project(
                            project_id=project.id,
                            user_id=participant.id,
                        )
                        or []
                    )

                    participants.append(
                        Participant(
                            id=participant.id,
                            first_name=participant.first_name,
                            last_name=participant.last_name,
                            roles=roles,
                        )
                    )

                info_project = Project(
                    id=project.id,
                    name=project.name,
                    description=project.description or "",
                    team_leader=info_teamlead,
                    participants=participants,
                )

                return InvitationResponse(
                    invitation_id=invitation.id,
                    notification_id=notification.id,
                    status=invitation.status,
                    project=info_project,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get invitation info")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get invitation info",
                ) from e

    @classmethod
    async def accept_invitation(
        cls,
        notification_id: UUID,
        user_id: UUID,
    ) -> BasicResponse:
        async with get_uow() as uow:
            try:
                ctx = await InvitationUtils.load_invitation_context(uow, notification_id, user_id)
                invitation = ctx.invitation

                if invitation.status != InvitationStatus.Posted:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Invitation is not in 'posted' status",
                    )

                active_project = await uow.projects.get_active_project_by_user_id(user_id)
                if active_project:
                    await uow.invitations.update(
                        invitation.id,
                        {"status": InvitationStatus.Rejected},
                    )
                    await uow.commit()
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User already has an active project",
                    )

                other_invitations = await uow.invitations.get_posted_for_user_excluding(
                    user_id=user_id,
                    exclude_invitation_id=invitation.id,
                )
                for inv in other_invitations:
                    await uow.invitations.update(
                        inv.id,
                        {"status": InvitationStatus.Rejected},
                    )
                    await uow.teams.delete_member(
                        project_id=inv.project_id,
                        user_id=user_id,
                    )
                    await uow.project_roles.delete_all_roles(
                        project_id=inv.project_id,
                        user_id=user_id,
                    )

                await uow.invitations.update(
                    invitation.id,
                    {"status": InvitationStatus.Accepted},
                )

                team_row = await uow.teams.get_by_project_and_user(
                    project_id=invitation.project_id,
                    user_id=user_id,
                )
                if not team_row:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Team row not found for invited user",
                    )

                if team_row.status != UserStatus.Invited:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User is not in 'invited' status in team",
                    )

                await uow.teams.update(
                    team_row.id,
                    {"status": UserStatus.Member},
                )
                await uow.users.mark_in_team(
                    user_id=user_id,
                    bool_team=True,
                )

                await uow.commit()

                return BasicResponse(
                    success=True,
                    message="Invitation accepted",
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during accept invitation")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during accept invitation",
                ) from e

    @classmethod
    async def reject_invitation(
        cls,
        notification_id: UUID,
        user_id: UUID,
    ) -> BasicResponse:
        async with get_uow() as uow:
            try:
                ctx = await InvitationUtils.load_invitation_context(uow, notification_id, user_id)
                invitation = ctx.invitation

                if invitation.status != InvitationStatus.Posted:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Invitation is not in 'posted' status",
                    )

                await uow.invitations.update(
                    invitation.id,
                    {"status": InvitationStatus.Rejected},
                )
                await uow.teams.delete_member(
                    project_id=invitation.project_id,
                    user_id=user_id,
                )
                await uow.project_roles.delete_all_roles(
                    project_id=invitation.project_id,
                    user_id=user_id,
                )

                await uow.commit()

                return BasicResponse(
                    success=True,
                    message="Invitation rejected",
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during reject invitation")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during reject invitation",
                ) from e
