# import pytest
# # from httpx import AsyncClient
# from fastapi.websockets import WebSocket
# from starlette.testclient import TestClient
# #
# #
# async def test_ws_session(test_client: TestClient, create_session: str):
#     # На бекенде создается сессия
#     session_id = create_session
#     # Клиент подключается к вебсокету
#     # Еще один клиент подключается к вебсокету
#     # Один клиент отправляет сообщение
#     # Другой клиент получает это сообщение
#     client = test_client
#     with client.websocket_connect(f"/api/v1/session/ws/join_session/{session_id}") as websocket:
#         websocket.send_text("Chat message")
#         data = websocket.receive_text()
#
#         assert data is None
