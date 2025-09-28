from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

BASE_DIR = Path(__file__).parent.parent.parent
TOML_SETTINGS_PATH = BASE_DIR / "config.toml"


PathsSources: list[tuple[Path, type[PydanticBaseSettingsSource]]] = [
    (TOML_SETTINGS_PATH, TomlConfigSettingsSource),
]


class Minio(BaseModel):
    minio_endpoint: str = ""
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = ""
    minio_root_user: str = ""
    minio_root_password: str = ""


class Database(BaseModel):
    postgres_username: str = ""
    postgres_db: str = ""
    postgres_port: int = 5432
    postgres_host: str = ""
    postgres_password: str = ""

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def alembic_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}"
            f"@localhost:{self.postgres_port}/{self.postgres_db}"
        )


class Logging(BaseModel):
    level: str = "INFO"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        toml_file=TOML_SETTINGS_PATH,
    )

    database: Database = Database()
    minio: Minio = Minio()
    logging: Logging = Logging()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        active_sources = [method(settings_cls) for path, method in PathsSources if path.exists()]
        return EnvSettingsSource(settings_cls), *active_sources


settings = Config()
