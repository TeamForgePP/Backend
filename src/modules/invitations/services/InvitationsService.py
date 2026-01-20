from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from src.core.db.enums import InvitationStatus, UserStatus
from src.core.db.models import Invitations, Teams, Users
from src.core.db.UnitOfWork import UnitOfWork
from src.core.security.dependencies import PrincipalContext


class InvitationsService:
    INVITATION_TTL = timedelta(days=7)

    def __init__(self, *, uow: UnitOfWork, principal: PrincipalContext) -> None:
        self.uow = uow
        self.principal = principal
        self._user: Users | None = None

    def _now(self) -> datetime:
        return datetime.now(UTC)

    async def _current_user(self) -> Users:
        if self._user is not None:
            return self._user

        if self.principal.role != "user":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

        try:
            user_id = UUID(self.principal.sub)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token subject",
            ) from exc

        user = await self.uow.users.get_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="not authenticated",
            )

        self._user = user
        return user

    def _ensure_invited_user(self, invitation: Invitations, *, user: Users) -> None:
        if invitation.invited_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    def _ensure_pending(self, invitation: Invitations) -> None:
        if invitation.status != InvitationStatus.Posted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="приглашение не найдено или уже обработано",
            )

    def _compute_deadline(self, created_at: datetime) -> datetime:
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return created_at + self.INVITATION_TTL

    async def get_invitation_info(self, invitation_id: UUID) -> dict:
        user = await self._current_user()

        invitation = await self.uow.invitations.get_by_id(invitation_id=invitation_id)
        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="приглашение не найдено или уже обработано",
            )

        self._ensure_invited_user(invitation, user=user)
        self._ensure_pending(invitation)

        notification = await self.uow.notifications.get_by_id(
            notification_id=invitation.notification_id
        )
        if notification is None or notification.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="приглашение не найдено или уже обработано",
            )

        project = await self.uow.projects.get_by_id(project_id=invitation.project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")

        teamlead = await self.uow.users.get_by_id(user_id=project.teamlead_id)
        if teamlead is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="teamlead not found")

        teamlead_roles = await self.uow.project_roles.get_roles_for_user_in_project(
            project_id=project.id, user_id=teamlead.id
        )

        stmt_participants = (
            select(Users)
            .join(Teams, Teams.user_id == Users.id)
            .where(
                Teams.project_id == project.id,
                Teams.status.in_([UserStatus.Owner, UserStatus.Member]),
            )
        )
        participants_users = (await self.uow.session.execute(stmt_participants)).scalars().all()
        participants: list[dict] = []
        for participant in participants_users:
            roles = await self.uow.project_roles.get_roles_for_user_in_project(
                project_id=project.id, user_id=participant.id
            )
            participants.append(
                {
                    "id": participant.id,
                    "first_name": participant.first_name,
                    "last_name": participant.last_name,
                    "roles": roles,
                }
            )

        return {
            "invitation_id": invitation.id,
            "notification_id": invitation.notification_id,
            "status": invitation.status,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description or "",
                "team_leader": {
                    "id": teamlead.id,
                    "first_name": teamlead.first_name,
                    "last_name": teamlead.last_name,
                    "roles": teamlead_roles,
                },
                "participants": participants,
            },
        }

    async def accept(self, invitation_id: UUID) -> dict:
        user = await self._current_user()

        invitation = await self.uow.invitations.get_by_id(invitation_id=invitation_id)
        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="приглашение не найдено или уже обработано",
            )

        self._ensure_invited_user(invitation, user=user)
        self._ensure_pending(invitation)

        deadline = self._compute_deadline(cast(datetime, invitation.created_at))
        if self._now() > deadline:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="срок действия приглашения истёк",
            )

        try:
            updated = await self.uow.invitations.update(
                invitation_id,
                {"status": InvitationStatus.Accepted},
            )
            if updated is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="приглашение не найдено или уже обработано",
                )

            notification = await self.uow.notifications.get_by_id(
                notification_id=invitation.notification_id
            )
            if notification is None or notification.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="приглашение не найдено или уже обработано",
                )

            await self.uow.notifications.update(invitation.notification_id, {"is_read": True})

            stmt_team = select(Teams).where(
                Teams.project_id == invitation.project_id,
                Teams.user_id == invitation.invited_user_id,
            )
            team = (await self.uow.session.execute(stmt_team)).scalar_one_or_none()

            if team is None:
                await self.uow.teams.create(
                    {
                        "project_id": invitation.project_id,
                        "user_id": invitation.invited_user_id,
                        "status": UserStatus.Member,
                        "created_at": self._now(),
                    }
                )
            elif team.status == UserStatus.Invited:
                await self.uow.teams.update(team.id, {"status": UserStatus.Member})

            user.in_team = True
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        return {"success": True, "message": "Invitation accepted"}

    async def decline(self, invitation_id: UUID) -> dict:
        user = await self._current_user()

        invitation = await self.uow.invitations.get_by_id(invitation_id=invitation_id)
        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="приглашение не найдено или уже обработано",
            )

        self._ensure_invited_user(invitation, user=user)
        self._ensure_pending(invitation)

        try:
            updated = await self.uow.invitations.update(
                invitation_id,
                {"status": InvitationStatus.Rejected},
            )
            if updated is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="приглашение не найдено или уже обработано",
                )

            notification = await self.uow.notifications.get_by_id(
                notification_id=invitation.notification_id
            )
            if notification is None or notification.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="приглашение не найдено или уже обработано",
                )

            await self.uow.notifications.update(invitation.notification_id, {"is_read": True})
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        return {"success": True, "message": "Invitation declined"}

    async def accepted_deadline(self, invitation_id: UUID) -> dict:
        user = await self._current_user()

        invitation = await self.uow.invitations.get_by_id(invitation_id=invitation_id)
        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="приглашение не найдено или уже обработано",
            )

        self._ensure_invited_user(invitation, user=user)
        self._ensure_pending(invitation)

        deadline = self._compute_deadline(cast(datetime, invitation.created_at))
        is_expired = self._now() > deadline

        return {
            "invitation_id": invitation.id,
            "accepted_deadline": deadline,
            "is_expired": is_expired,
        }
