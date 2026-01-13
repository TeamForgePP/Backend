from fastapi import Response

from src.config import cfg
from src.modules.auth.schemas.user import UserTokenPair


def set_user_cookies(response: Response, tokens: UserTokenPair) -> None:
    response.set_cookie(
        key=cfg.user_cookies.access,
        value=tokens.access_token,
        httponly=True,
        secure=False,  # на проде True + https
        samesite="lax",
        max_age=cfg.jwt.access_cookie_max_age,
        path="/",
    )

    response.set_cookie(
        key=cfg.user_cookies.refresh,
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=cfg.jwt.refresh_cookie_max_age,
        path="/",
    )


def clear_user_cookies(response: Response) -> None:
    response.delete_cookie(cfg.user_cookies.access, path="/")
    response.delete_cookie(cfg.user_cookies.refresh, path="/")
