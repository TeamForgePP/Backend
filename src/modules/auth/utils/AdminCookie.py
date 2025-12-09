from fastapi import Response

from src.config import cfg
from src.modules.auth.schemas import AdminTokenPair


def set_admin_cookies(response: Response, tokens: AdminTokenPair) -> None:
    response.set_cookie(
        key=cfg.admin.cookies.access,
        value=tokens.access_token,
        httponly=True,
        secure=False,  # на локалке можно False, если без https
        samesite="lax",
        max_age=cfg.jwt.access_token_minutes,  # уже в секундах
        path="/",
    )

    response.set_cookie(
        key=cfg.admin.cookies.refresh,
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=cfg.jwt.refresh_token_days,  # тоже секунды
        path="/",
    )


def clear_admin_cookies(response: Response) -> None:
    response.delete_cookie(cfg.admin.cookies.access, path="/")
    response.delete_cookie(cfg.admin.cookies.refresh, path="/")
