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
    minio_bucket: str = "public"
    upload_expire_seconds: int = 900
    max_file_size_mb: int = 50

    @property
    def max_file_size_bytes(self) -> int:
        return int(self.max_file_size_mb) * 1024 * 1024


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
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


class Logging(BaseModel):
    level: str = "INFO"


class AdminCookies(BaseModel):
    access: str = "admin_access_token"
    refresh: str = "admin_refresh_token"


class Admin(BaseModel):
    login: str = ""
    password: str = ""
    cookies: AdminCookies = AdminCookies()


class UserCookies(BaseModel):
    access: str = "user_access_token"
    refresh: str = "user_refresh_token"


class JWT(BaseModel):
    secret: str = ""
    algorithm: str = "HS256"
    access_token_minutes: int = 1800
    refresh_token_days: int = 604800

    @property
    def access_cookie_max_age(self) -> int:
        return self.access_token_minutes * 60

    @property
    def refresh_cookie_max_age(self) -> int:
        return self.refresh_token_days * 24 * 60 * 60


class Redis(BaseModel):
    url: str = "redis://localhost:6379/0"
    login_attempts_prefix: str = "auth:login_attempts:"
    login_attempts_ttl_seconds: int = 300
    login_attempts_max: int = 5


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        toml_file=TOML_SETTINGS_PATH,
    )

    database: Database = Database()
    minio: Minio = Minio()
    logging: Logging = Logging()
    admin: Admin = Admin()
    user_cookies: UserCookies = UserCookies()
    jwt: JWT = JWT()
    redis: Redis = Redis()

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


cfg = Config()
