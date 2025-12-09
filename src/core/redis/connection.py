from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis.asyncio import Redis, from_url

from src.config import cfg

_redis: Redis | None = None


async def init_redis() -> None:
    global _redis

    if _redis is None:
        _redis = from_url(
            cfg.redis.url,
            encoding="utf-8",
            decode_responses=True,
        )


async def close_redis() -> None:
    global _redis

    if _redis is not None:
        await _redis.close()
        _redis = None


def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis is not initialized. Call init_redis() in lifespan.")
    return _redis


@asynccontextmanager
async def redis_context() -> AsyncIterator[Redis]:
    client = get_redis()
    try:
        yield client
    finally:
        ...
