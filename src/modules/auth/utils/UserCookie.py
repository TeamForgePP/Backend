from fastapi import Response

from src.config import cfg
from src.modules.auth.schemas.user import UserTokenPair

COOKIE_DOMAIN = ".team-forge.ru"


def set_user_cookies(response: Response, tokens: UserTokenPair) -> None:
    response.set_cookie(
        key=cfg.cookies.user.access,
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=cfg.jwt.access_cookie_max_age,
        path="/",
        domain=COOKIE_DOMAIN,
    )
    response.set_cookie(
        key=cfg.cookies.user.refresh,
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=cfg.jwt.refresh_cookie_max_age,
        path="/",
        domain=COOKIE_DOMAIN,
    )


def clear_user_cookies(response: Response) -> None:
    response.delete_cookie(cfg.cookies.user.access, path="/", domain=COOKIE_DOMAIN)
    response.delete_cookie(cfg.cookies.user.refresh, path="/", domain=COOKIE_DOMAIN)
