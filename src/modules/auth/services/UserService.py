import logging
from typing import Any

from fastapi import HTTPException, Request, Response, status

from src.config import cfg
from src.core.db import get_uow
from src.core.logger import get_logger
from src.core.redis.login_attempts import LoginAttemptsService
from src.core.redis.uow import RedisUnitOfWork
from src.modules.admin.utils.user_hash import verify_password
from src.modules.auth.schemas.user import UserLoginRequest, UserTokenPair
from src.modules.auth.utils.UserCookie import clear_user_cookies, set_user_cookies
from src.modules.auth.utils.UserToken import get_user_token_service

logger = get_logger("auth.user")
logger.setLevel(logging.INFO)


class UserAuthService:
    @classmethod
    async def login(
        cls,
        request: Request,
        data: UserLoginRequest,
        response: Response,
    ) -> UserTokenPair:
        redis_uow = RedisUnitOfWork()
        attempts_service = LoginAttemptsService(redis_uow.redis)

        identifier = str(data.email)
        client_ip = request.client.host if request.client else "unknown"

        if await attempts_service.is_blocked(identifier):
            ttl = await attempts_service.get_ttl(identifier)
            logger.warning(
                "blocked user login attempt | email=%s | ip=%s | remaining_block_sec=%s",
                identifier,
                client_ip,
                ttl,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many login attempts, try again later",
            )

        async with get_uow() as uow:
            user = await uow.users.get_by_email(data.email)

        if user is None:
            attempts = await attempts_service.increment(identifier, ip=client_ip)
            logger.warning(
                "failed user login (no such email) | email=%s | ip=%s | attempts=%s",
                identifier,
                client_ip,
                attempts,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"invalid credentials (attempts: {attempts})",
            )

        hashed_password = user.password

        if not verify_password(data.password, hashed_password):
            attempts = await attempts_service.increment(identifier, ip=client_ip)
            logger.warning(
                "failed user login (bad password) | email=%s | ip=%s | attempts=%s",
                identifier,
                client_ip,
                attempts,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"invalid credentials (attempts: {attempts})",
            )

        await attempts_service.reset(identifier)

        logger.info(
            "user login success | user_id=%s | email=%s | ip=%s",
            user.id,
            identifier,
            client_ip,
        )

        token_service = get_user_token_service()
        user_id_str = str(user.id)

        tokens = UserTokenPair(
            access_token=token_service.create_access(
                user_id=user_id_str,
                email=user.email,
            ),
            refresh_token=token_service.create_refresh(
                user_id=user_id_str,
                email=user.email,
            ),
        )

        set_user_cookies(response, tokens)
        return tokens

    @classmethod
    def refresh(cls, request: Request, response: Response) -> UserTokenPair:
        client_ip = request.client.host if request.client else "unknown"

        refresh_cookie_name = cfg.user.cookies.refresh
        refresh_token = request.cookies.get(refresh_cookie_name)

        if not refresh_token:
            logger.warning("user refresh without token | ip=%s", client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="refresh token missing",
            )

        token_service = get_user_token_service()

        try:
            payload: dict[str, Any] = token_service.decode(refresh_token)
        except Exception as err:
            logger.warning("user refresh invalid token | ip=%s", client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid refresh token",
            ) from err

        if not token_service.is_user_refresh(payload):
            logger.warning("user refresh rejected | ip=%s", client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="refresh token rejected",
            )

        user_id = str(payload["sub"])
        email = str(payload["email"])

        tokens = UserTokenPair(
            access_token=token_service.create_access(
                user_id=user_id,
                email=email,
            ),
            refresh_token=token_service.create_refresh(
                user_id=user_id,
                email=email,
            ),
        )

        logger.info(
            "user token refreshed | user_id=%s | email=%s | ip=%s",
            user_id,
            email,
            client_ip,
        )

        set_user_cookies(response, tokens)
        return tokens

    @classmethod
    def logout(cls, response: Response) -> None:
        clear_user_cookies(response)
