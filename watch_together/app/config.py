from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # noqa: E701,E261

    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT")

    verify_token_url: str = Field(alias="VERIFY_TOKEN_URL")
    get_user_friends_url: str = Field(alias="GET_USER_FRIENDS_URL")

    mongo_conn: str = Field(alias="MONGO_CONN", default="mongodb://admin:admin@localhost:27017/")  # noqa: E701,E261


settings = Settings()


def get_settings() -> Settings:
    return settings
