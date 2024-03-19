from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    db_user: str = Field(default="app", alias="POSTGRES_USER")
    db_password: str = Field(default="123qwe", alias="POSTGRES_PASSWORD")
    db_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    db_port: int = Field(default="5432", alias="POSTGRES_PORT")
    db_name: str = Field(default="auth_database", alias="POSTGRES_DB")
    # Services hosts
    api_host: str = "http://localhost"
    api_port: int = 8000

    # Faker
    random_seed: int = 42


settings = TestSettings()
