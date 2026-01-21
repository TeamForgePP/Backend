import logging
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import get_uow
from src.core.logger import get_logger
from src.modules.notifications.shemas import BasicResponse, Notification, NotificationsResponse

logger = get_logger("notifications.service")
logger.setLevel(logging.INFO)


class NotificationsService:
    @classmethod
    async def get_notifications_info(cls, user_id: UUID) -> NotificationsResponse:
        async with get_uow() as uow:
            try:
                all_notifications = await uow.notifications.get_by_user_id(user_id)
                if not all_notifications:
                    return NotificationsResponse(notifications=[], unread_count=0)

                notifications: list[Notification] = []
                unread = 0

                for notification in all_notifications:
                    invitation = await uow.invitations.get_by_notification_id(notification.id)

                    notifications.append(
                        Notification(
                            id=notification.id,
                            type=notification.type,
                            title=notification.title,
                            message=notification.message,
                            is_read=notification.is_read,
                            created_at=notification.created_at,  # type: ignore
                            invitation_id=invitation.id if invitation else None,
                        )
                    )

                    if not notification.is_read:
                        unread += 1

                return NotificationsResponse(notifications=notifications, unread_count=unread)

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during get notifications info")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get notifications info",
                ) from e

    @classmethod
    async def read_all(cls, user_id: UUID) -> BasicResponse:
        async with get_uow() as uow:
            try:
                all_notifications = await uow.notifications.get_by_user_id(user_id)
                if not all_notifications:
                    return BasicResponse(
                        success=True, message="All notifications read successfully"
                    )

                for notification in all_notifications:
                    if notification.is_read:
                        continue
                    await uow.notifications.update(notification.id, {"is_read": True})

                await uow.commit()
                return BasicResponse(success=True, message="All notifications read successfully")

            except HTTPException:
                raise
            except Exception as e:
                logger.exception("Error during read_all")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during read_all",
                ) from e
