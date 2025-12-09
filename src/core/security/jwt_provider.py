from datetime import UTC, datetime, timedelta
from typing import Any, Literal, cast

from jose import jwt

from src.config import cfg

TokenType = Literal["access", "refresh"]


class JwtProvider:
    def __init__(self) -> None:
        self._secret = cfg.jwt.secret
        self._algorithm = cfg.jwt.algorithm

    def encode(
        self,
        *,
        sub: str,
        token_type: TokenType,
        expires_delta: timedelta,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(UTC)

        payload: dict[str, Any] = {
            "sub": sub,
            "typ": token_type,
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
        }

        if extra_claims:
            payload.update(extra_claims)

        token = jwt.encode(payload, self._secret, algorithm=self._algorithm)
        return cast(str, token)

    def decode(self, token: str) -> dict[str, Any]:
        payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        return cast(dict[str, Any], payload)


_jwt_provider: JwtProvider | None = None


def get_jwt_provider() -> JwtProvider:
    global _jwt_provider
    if _jwt_provider is None:
        _jwt_provider = JwtProvider()
    return _jwt_provider
