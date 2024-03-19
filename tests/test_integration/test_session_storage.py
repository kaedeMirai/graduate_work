import json
import httpx

from watch_together.app.services.sessions import get_active_sessions
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport


async def test_session_restore(api_client, test_app):
    # Пользователи должны подключаться к упавшей сессии
    # Создаем сессию через эндпоинт
    response = await api_client.post(
        url="/api/v1/session/create_session",
        headers={"Authorization": "Bearer some-token"},
        data=json.dumps(["string"]),
    )
    session_id = response.json()["session_id"]
    assert session_id is not None

    # Останавливаем сервер ? - Можно имитировать это очищением объекта active_sessions
    active_sessions = await get_active_sessions()
    active_sessions.clear()

    assert await get_active_sessions() == {}

    # Подключаемся заново - Тут объект должен будет взят из Монго и есть возможность отправить сообщение
    async with httpx.AsyncClient(transport=ASGIWebSocketTransport(test_app)) as client:
        uri = f"http://localhost:8090/api/v1/session/ws/join_session/{session_id}"
        async with aconnect_ws(uri, client) as ws:
            await ws.send_text("test text")
