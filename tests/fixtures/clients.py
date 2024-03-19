import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI

from watch_together.app.main import build_app
from watch_together.app.utils.auth_util import get_current_user, get_user_friends
from watch_together.app.config import get_settings

from tests.settings import settings, get_test_settings
from tests.utils.users import get_user_test, get_user_friends_test


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    app = build_app()
    app.dependency_overrides[get_current_user] = get_user_test
    app.dependency_overrides[get_user_friends] = get_user_friends_test
    app.dependency_overrides[get_settings] = get_test_settings
    return app


@pytest_asyncio.fixture(scope="session")
async def api_client(test_app: FastAPI) -> AsyncClient:
    client = AsyncClient(
        app=test_app,
        base_url=f"{settings.api_host}:{settings.api_port}",
    )
    yield client
