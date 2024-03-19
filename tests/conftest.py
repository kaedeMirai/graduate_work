import asyncio

import pytest

from httpx import AsyncClient

pytest_plugins = [
    "tests.fixtures.clients",
]


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def create_session(api_client: AsyncClient) -> str:
    response = await api_client.post("/api/v1/session/create_session")
    return response.json()["session_id"]
