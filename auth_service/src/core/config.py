from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = Field(alias="POSTGRES_USER")
    db_password: str = Field(alias="POSTGRES_PASSWORD")
    db_host: str = Field(alias="POSTGRES_HOST")
    db_port: int = Field(alias="POSTGRES_PORT")
    db_name: str = Field(alias="POSTGRES_DB")

    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT")

    fastapi_host: str = Field(alias="FASTAPI_HOST")
    fastapi_port: int = Field(alias="FASTAPI_PORT")

    access_token_expire_time: int = Field(10, alias="ACCESS_TOKEN_EXPIRE_TIME")
    refresh_token_expire_time: int = Field(60, alias="REFRESH_TOKEN_EXPIRE_TIME")
    auth_jwt_key: str = Field(alias="AUTH_JWT_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")

    yandex_secret_id: str = Field(alias="YANDEX_SECRET_ID")

    jaeger_host: str = Field(alias="JAEGER_HOST")
    jaeger_port: int = Field(alias="JAEGER_PORT")
    activate_telemetry: bool = Field(default=True, alias="ACTIVATE_TELEMETRY")

    def build_db_connection_uri(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            user or self.db_user,
            password or self.db_password,
            host or self.db_host,
            port or self.db_port,
            database or self.db_name,
        )

    class Config:
        env_file = "../.env"


settings = Settings()
