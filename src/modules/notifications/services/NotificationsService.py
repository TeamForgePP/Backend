import logging
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import get_uow
from src.core.logger import get_logger
from src.modules.notifications.shemas import (
    BasicResponse,
    InvitationResponse,
    Notification,
    NotificationsResponse,
    Participant,
    Project,
    TeamLeader,
)

logger = get_logger("notifications.service")
logger.setLevel(logging.INFO)


class NotificationsService:
    # ---------------- GET ---------------- #
    @classmethod
    async def get_notifications_info(cls, user_id: UUID) -> NotificationsResponse:
        async with get_uow() as uow:
            try:
                logger.info("get_notifications_info started")

                all_notifications = await uow.notifications.get_by_user_id(user_id)
                if not all_notifications:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Notifications not found"
                    )

                notifications: list[Notification] = []
                unread = 0
                for notification in all_notifications:
                    invitation = await uow.invitations.get_by_notification_id(notification.id)
                    if not invitation:
                        info = Notification(
                            id=notification.id,
                            type=notification.type,
                            title=notification.title,
                            message=notification.message,
                            is_read=notification.is_read,
                            created_at=notification.created_at,  # type: ignore
                            invitation_id=None,
                        )
                    else:
                        info = Notification(
                            id=notification.id,
                            type=notification.type,
                            title=notification.title,
                            message=notification.message,
                            is_read=notification.is_read,
                            created_at=notification.created_at,  # type: ignore
                            invitation_id=invitation.id,
                        )

                    if not notification.is_read:
                        unread += 1

                    notifications.append(info)

                return NotificationsResponse(notifications=notifications, unread_count=unread)

            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    @classmethod
    async def get_invitation_info(cls, invitation_id: UUID) -> InvitationResponse:
        async with get_uow() as uow:
            try:
                logger.info("get_notifications_info started")

                invitation = await uow.invitations.get_by_id(invitation_id=invitation_id)
                if not invitation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
                    )

                notification = await uow.notifications.get_by_id(
                    notification_id=invitation.notification_id
                )
                if not notification:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
                    )

                project = await uow.projects.get_by_id(project_id=notification.project_id)
                if not project:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                    )

                teamlead = await uow.users.get_by_id(user_id=project.teamlead_id)
                if not teamlead:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Teamlead not found"
                    )
                roles_teamlead = await uow.project_roles.get_roles_for_user_in_project(
                    project_id=project.id, user_id=teamlead.id
                )
                info_teamlead = TeamLeader(
                    id=teamlead.id,
                    first_name=teamlead.first_name,
                    last_name=teamlead.last_name,
                    roles=roles_teamlead,
                )

                members = await uow.users.get_by_project_id(project_id=project.id)
                participants: list[Participant] = []
                for participant in members:
                    roles = await uow.project_roles.get_roles_for_user_in_project(
                        project_id=project.id, user_id=participant.id
                    )
                    info_part = Participant(
                        id=participant.id,
                        first_name=participant.first_name,
                        last_name=participant.last_name,
                        roles=roles,
                    )
                    participants.append(info_part)

                info_project = Project(
                    id=project.id,
                    name=project.name,
                    description=project.description or "",
                    team_leader=info_teamlead,
                    participants=participants,
                )
                info = InvitationResponse(
                    invitation_id=invitation_id,
                    notification_id=invitation.notification_id,
                    status=invitation.status,
                    project=info_project,
                )

                return info

            except Exception as e:
                logger.error("Error during get info: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get info",
                ) from e

    # ---------------- PACTH ---------------- #

    @classmethod
    async def read_all(cls, user_id: UUID) -> BasicResponse:
        async with get_uow() as uow:
            logger.info("read_all started")

            all_notifications = await uow.notifications.get_by_user_id(user_id)

            for notification in all_notifications:
                data = {
                    "id": notification.id,
                    "user_id": notification.user_id,
                    "type": notification.type,
                    "title": notification.title,
                    "message": notification.message,
                    "project_id": notification.project_id,
                    "is_read": True,
                    "created_at": notification.created_at,
                }

                await uow.notifications.update(notification.id, data)

            await uow.commit()
            return BasicResponse(success=True, message="All notifications read successfully")
