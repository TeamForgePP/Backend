from datetime import timedelta
from typing import Any, Protocol

from src.config import cfg
from src.core.security.jwt_provider import JwtProvider, get_jwt_provider
from src.core.security.TokenType import TokenType


class _ProviderProtocol(Protocol):
    def encode(
        self,
        *,
        sub: str,
        token_type: TokenType,
        expires_delta: timedelta,
        extra_claims: dict[str, Any] | None = None,
    ) -> str: ...

    def decode(self, token: str) -> dict[str, Any]: ...


class AdminTokenService:
    def __init__(self, provider: JwtProvider | None = None) -> None:
        # Теперь тип совместим
        self._provider: _ProviderProtocol = provider or get_jwt_provider()

        # Исправлено: timedelta требует seconds? Нет — должны быть minutes/days
        self._access_ttl = timedelta(minutes=cfg.jwt.access_token_minutes)
        self._refresh_ttl = timedelta(days=cfg.jwt.refresh_token_days)

        self._subject = "admin"

    def create_access(self) -> str:
        return self._provider.encode(
            sub=self._subject,
            token_type="access",
            expires_delta=self._access_ttl,
            extra_claims={"role": "admin"},
        )

    def create_refresh(self) -> str:
        return self._provider.encode(
            sub=self._subject,
            token_type="refresh",
            expires_delta=self._refresh_ttl,
            extra_claims={"role": "admin"},
        )

    def decode(self, token: str) -> dict[str, Any]:
        return self._provider.decode(token)

    def is_admin_access(self, payload: dict[str, Any]) -> bool:
        return payload.get("sub") == self._subject and payload.get("typ") == "access"

    def is_admin_refresh(self, payload: dict[str, Any]) -> bool:
        return payload.get("sub") == self._subject and payload.get("typ") == "refresh"


_admin_service: AdminTokenService | None = None


def get_admin_token_service() -> AdminTokenService:
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminTokenService()
    return _admin_service
