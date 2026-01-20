import logging
from typing import Any

from fastapi import HTTPException, Request, Response, status

from src.config import cfg
from src.core.logger import get_logger
from src.core.redis.login_attempts import LoginAttemptsService
from src.core.redis.uow import RedisUnitOfWork
from src.modules.auth.schemas import AdminLoginRequest, AdminTokenPair
from src.modules.auth.utils import (
    clear_admin_cookies,
    get_admin_token_service,
    set_admin_cookies,
)

logger = get_logger("auth.admin")
logger.setLevel(logging.INFO)


class AdminAuthService:
    @classmethod
    async def login(
        cls,
        request: Request,
        data: AdminLoginRequest,
        response: Response,
    ) -> AdminTokenPair:
        redis_uow = RedisUnitOfWork()
        attempts_service = LoginAttemptsService(redis_uow.redis)

        identifier = data.username
        client_ip = request.client.host if request.client else "unknown"

        if await attempts_service.is_blocked(identifier):
            ttl = await attempts_service.get_ttl(identifier)
            logger.warning(
                "blocked admin login attempt | username=%s | ip=%s | remaining_block_sec=%s",
                identifier,
                client_ip,
                ttl,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many login attempts, try again later",
            )

        if data.username != cfg.admin.login or data.password != cfg.admin.password:
            attempts = await attempts_service.increment(identifier, ip=client_ip)
            logger.warning(
                "failed admin login | username=%s | ip=%s | attempts=%s",
                identifier,
                client_ip,
                attempts,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"invalid admin credentials (attempts: {attempts})",
            )

        await attempts_service.reset(identifier)

        logger.info(
            "admin login success | username=%s | ip=%s",
            identifier,
            client_ip,
        )

        token_service = get_admin_token_service()

        tokens = AdminTokenPair(
            access_token=token_service.create_access(),
            refresh_token=token_service.create_refresh(),
        )

        set_admin_cookies(response, tokens)
        return tokens

    @classmethod
    def refresh(cls, request: Request, response: Response) -> AdminTokenPair:
        client_ip = request.client.host if request.client else "unknown"

        refresh_cookie_name = cfg.cookies.admin.refresh
        refresh_token = request.cookies.get(refresh_cookie_name)

        if not refresh_token:
            logger.warning(
                "admin refresh without token | ip=%s",
                client_ip,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="refresh token missing",
            )

        token_service = get_admin_token_service()

        try:
            payload: dict[str, Any] = token_service.decode(refresh_token)
        except Exception as err:
            logger.warning(
                "admin refresh invalid token | ip=%s",
                client_ip,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid refresh token",
            ) from err

        if not token_service.is_admin_refresh(payload):
            logger.warning(
                "admin refresh rejected | ip=%s",
                client_ip,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="refresh token rejected",
            )

        tokens = AdminTokenPair(
            access_token=token_service.create_access(),
            refresh_token=token_service.create_refresh(),
        )

        logger.info(
            "admin token refreshed | ip=%s",
            client_ip,
        )

        set_admin_cookies(response, tokens)
        return tokens

    @classmethod
    def logout(cls, response: Response) -> None:
        clear_admin_cookies(response)
