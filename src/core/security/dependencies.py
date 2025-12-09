from dataclasses import dataclass
from typing import Any, Literal, TypedDict, cast

from fastapi import Depends, HTTPException, Request, status

from src.config import cfg
from src.core.security.TokenType import TokenType
from src.modules.auth.utils.AdminToken import get_admin_token_service

Role = Literal["admin", "user"]


class RawPayload(TypedDict, total=False):
    sub: str
    typ: TokenType
    role: Role
    iat: int
    exp: int


@dataclass
class AccessContext:
    sub: str
    role: Role
    token_type: TokenType


def _get_raw_token_from_cookies(request: Request) -> str:
    cookie_name = cfg.admin.cookies.access
    token = request.cookies.get(cookie_name)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )

    return token


def get_access_context(request: Request) -> AccessContext:
    token = _get_raw_token_from_cookies(request)
    admin_token_service = get_admin_token_service()

    try:
        payload_dict = admin_token_service.decode(token)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        ) from err

    raw_payload_dict = cast(dict[str, Any], payload_dict)
    payload = cast(RawPayload, raw_payload_dict)

    if admin_token_service.is_admin_access(raw_payload_dict):
        role: Role = "admin"
        token_type: TokenType = TokenType.ADMIN_ACCESS
    elif admin_token_service.is_admin_refresh(raw_payload_dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token is not allowed here",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token rejected",
        )

    sub = payload.get("sub", "admin")

    return AccessContext(
        sub=sub,
        role=role,
        token_type=token_type,
    )


access_context_dep = Depends(get_access_context)


def require_admin(access: AccessContext = access_context_dep) -> AccessContext:
    if access.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin only",
        )

    return access
