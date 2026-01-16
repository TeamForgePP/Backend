from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.logger import setup_logging
from src.core.redis.connection import close_redis, init_redis
from src.modules.router import router as api_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_redis()

    try:
        yield
    finally:
        await close_redis()


app = FastAPI(
    title="TeamForge",
    lifespan=lifespan,
)

app.include_router(api_router)

app.add_middleware(
    cast(Any, CORSMiddleware), allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
async def ping() -> str:
    return "pong"
