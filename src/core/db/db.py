from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import cfg

async_engine = create_async_engine(cfg.database.async_database_url, echo=False)

Session = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=False,
)
