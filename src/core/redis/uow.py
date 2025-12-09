from redis.asyncio import Redis

from src.core.redis.connection import get_redis


class RedisUnitOfWork:
    def __init__(self, client: Redis | None = None) -> None:
        self._client: Redis = client or get_redis()

    async def __aenter__(self) -> "RedisUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        return None

    @property
    def redis(self) -> Redis:
        return self._client
