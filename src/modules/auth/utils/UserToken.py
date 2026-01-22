from datetime import timedelta
from typing import Any, Protocol

from src.config import cfg
from src.core.security.jwt_provider import JwtProvider, TokenType, get_jwt_provider


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


class UserTokenService:
    def __init__(self, provider: JwtProvider | None = None) -> None:
        self._provider: _ProviderProtocol = provider or get_jwt_provider()

        self._access_ttl = timedelta(minutes=cfg.jwt.access_token_minutes)
        self._refresh_ttl = timedelta(days=cfg.jwt.refresh_token_days)

    def create_access(self, user_id: str, email: str) -> str:
        return self._provider.encode(
            sub=user_id,
            token_type="access",
            expires_delta=self._access_ttl,
            extra_claims={"role": "user", "email": email},
        )

    def create_refresh(self, user_id: str, email: str) -> str:
        return self._provider.encode(
            sub=user_id,
            token_type="refresh",
            expires_delta=self._refresh_ttl,
            extra_claims={"role": "user", "email": email},
        )

    def decode(self, token: str) -> dict[str, Any]:
        return self._provider.decode(token)

    def is_user_access(self, payload: dict[str, Any]) -> bool:
        return payload.get("typ") == "access" and payload.get("role") == "user"

    def is_user_refresh(self, payload: dict[str, Any]) -> bool:
        return payload.get("typ") == "refresh" and payload.get("role") == "user"


_user_service: UserTokenService | None = None


def get_user_token_service() -> UserTokenService:
    global _user_service
    if _user_service is None:
        _user_service = UserTokenService()
    return _user_service
