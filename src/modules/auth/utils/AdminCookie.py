from fastapi import Response

from src.config import cfg
from src.modules.auth.schemas import AdminTokenPair


def set_admin_cookies(response: Response, tokens: AdminTokenPair) -> None:
    response.set_cookie(
        key=cfg.cookies.admin.access,
        value=tokens.access_token,
        httponly=True,
        secure=False,  # локально можно False, под https лучше True
        samesite="lax",
        max_age=cfg.jwt.access_cookie_max_age,
        path="/",
    )

    response.set_cookie(
        key=cfg.cookies.admin.refresh,
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=cfg.jwt.refresh_cookie_max_age,
        path="/",
    )


def clear_admin_cookies(response: Response) -> None:
    response.delete_cookie(cfg.cookies.admin.access, path="/")
    response.delete_cookie(cfg.cookies.admin.refresh, path="/")
