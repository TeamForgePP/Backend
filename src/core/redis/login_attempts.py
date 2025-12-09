import logging
from typing import cast

from redis.asyncio import Redis

from src.config import cfg
from src.core.logger import get_logger

logger = get_logger("auth.login_attempts")
logger.setLevel(logging.INFO)


class LoginAttemptsService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis
        self._prefix = cfg.redis.login_attempts_prefix
        self._ttl = cfg.redis.login_attempts_ttl_seconds
        self._max_attempts = cfg.redis.login_attempts_max

    def _key(self, identifier: str) -> str:
        return f"{self._prefix}{identifier}"

    async def increment(self, identifier: str, *, ip: str | None = None) -> int:
        key = self._key(identifier)
        value = cast(int, await self._redis.incr(key))

        if value == 1:
            await self._redis.expire(key, self._ttl)

        if value >= self._max_attempts:
            ttl = await self.get_ttl(identifier)
            logger.warning(
                "admin login blocked | identifier=%s | ip=%s | attempts=%s | ttl_sec=%s",
                identifier,
                ip or "-",
                value,
                ttl,
            )

        return int(value)

    async def get_attempts(self, identifier: str) -> int:
        raw = await self._redis.get(self._key(identifier))
        if raw is None:
            return 0

        if isinstance(raw, bytes):
            try:
                return int(raw.decode())
            except (ValueError, UnicodeDecodeError):
                return 0
        if isinstance(raw, str):
            try:
                return int(raw)
            except ValueError:
                return 0

        try:
            return int(raw)
        except Exception:
            return 0

    async def get_ttl(self, identifier: str) -> int | None:
        ttl_raw = await self._redis.ttl(self._key(identifier))

        ttl = cast(int, ttl_raw)
        if ttl is None or ttl < 0:
            return None
        return int(ttl)

    async def reset(self, identifier: str) -> None:
        await self._redis.delete(self._key(identifier))

    async def is_blocked(self, identifier: str) -> bool:
        attempts = await self.get_attempts(identifier)
        return attempts >= self._max_attempts
