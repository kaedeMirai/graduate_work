import json
from uuid import uuid4
from datetime import datetime

from fastapi import WebSocket, HTTPException, status
from fastapi.logger import logger
from redis.exceptions import ConnectionError

from watch_together.app.services.state_handle import StateHandler
from watch_together.app.models.sessions import Session
from watch_together.app.api.v1.sessions.schemas import AuthorResponse, MessageResponse
from watch_together.app.db.cache.redis_cache import AbstractCacheStorage


class ConnectionManager:

    def __init__(self, cache_storage: AbstractCacheStorage):
        self.cache_storage = cache_storage
        self.state_handler = StateHandler(cache_storage)

    async def connect(self, session: Session, websocket: WebSocket):
        await websocket.accept()
        session.clients.append(websocket)
        logger.info(f"New client: {websocket}")

        try:
            response_timestamp, response_status = await self.state_handler.handle_video_state(session, websocket)
            logger.info(f"Response timestamp: {response_timestamp}. Response status: {response_status}")
            if response_timestamp is not None and response_status is not None:
                await self.send_personal_message(response_timestamp.json(), session, websocket)
                await self.send_personal_message(response_status.json(), session, websocket)

            chat_state = await self.state_handler.handle_chat_state(session, websocket)
            logger.info(f"Chat state: {chat_state}.")
            if chat_state is not None:
                for message in chat_state:
                    await self.send_personal_message(message, session, websocket)
        except ConnectionError:
            logger.error("Redis is unavailable")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis is unavailable")

    async def disconnect(self, session: Session, websocket: WebSocket):
        session.clients.remove(websocket)
        await websocket.close()
        logger.info(f"Client disconnect: {websocket}")

    async def send_personal_message(self, message: str, session: Session, websocket: WebSocket):
        await websocket.send_text(message)
        logger.info(f"Sent message to: {websocket}")

    async def broadcast(self, message: str, session: Session, websocket: WebSocket):
        for client in session.clients:
            await client.send_text(message)
            logger.info(f"sent broadcast message to: {client}")

    async def handle_message(self, data: dict, session: Session, websocket: WebSocket):
        message_type = data.get("type")
        if message_type == "message":
            await self.handle_message_chat(data, session, websocket)
        elif message_type == "command":
            await self.handle_message_command(data, session, websocket)

    async def handle_message_chat(self, data: dict, session: Session, websocket: WebSocket):
        author_message = next((friend for friend in session.friends if friend["id"] == data["author_id"]), None)
        name = f"{author_message['first_name']} {author_message['last_name']}"
        author_response = AuthorResponse(id=data["author_id"], name=name)
        response = MessageResponse(
            author=author_response, message=data["message"], id=uuid4(), timestamp=str(datetime.now())
        )
        await self.broadcast(response.json(), session, websocket)
        try:
            await self.state_handler.save_message_to_cache(session, response)
        except ConnectionError:
            logger.error("Redis is unavailable")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis is unavailable")

    async def handle_message_command(self, data: dict, session: Session, websocket: WebSocket):
        response = {
            "userId": data["userId"],
            "type": data["type"],
            "commandType": data["commandType"],
            "timestamp": data["timestamp"],
        }
        await self.broadcast(json.dumps(response), session, websocket)
        try:
            await self.state_handler.save_command_to_cache(session, data)
        except ConnectionError:
            logger.error("Redis is unavailable")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis is unavailable")
