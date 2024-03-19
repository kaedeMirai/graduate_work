from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    api_host: str = "http://localhost"
    api_port: int = 8090

    mongo_conn: str = "mongodb://admin:admin@mongo:27017/"


settings = TestSettings()


def get_test_settings() -> TestSettings:
    return settings
