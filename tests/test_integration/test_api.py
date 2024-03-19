from http import HTTPStatus
from httpx import AsyncClient


async def test_create_session(api_client: AsyncClient):
    response = await api_client.post("/api/v1/session/create_session")
    assert response.status_code == HTTPStatus.OK
