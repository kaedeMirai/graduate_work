from datetime import datetime

from fastapi import WebSocket
from fastapi.logger import logger
from redis.exceptions import ConnectionError

from watch_together.app.models.sessions import Session
from watch_together.app.db.cache.abstract_cache import AbstractCacheStorage
from watch_together.app.api.v1.sessions.schemas import CommandResponse, MessageResponse


class StateHandler:

    def __init__(self, cache_storage: AbstractCacheStorage):
        self.cache_storage = cache_storage

    async def handle_video_state(self, session: Session, websocket: WebSocket):
        key = f"{session.session_id}:command"
        try:
            video_state = await self.cache_storage.hvals(key)
        except ConnectionError:
            logger.error("Redis is unavailable")
            return None, None

        if video_state:
            response_timestamp, response_status = await self.process_video_state(video_state, session, websocket)
            return response_timestamp, response_status
        return None, None

    async def process_video_state(self, video_state: list, session: Session, websocket: WebSocket):
        command_type = video_state[0].decode("utf-8")
        timestamp = float(video_state[1].decode("utf-8"))
        timestamp_action = video_state[2].decode("utf-8")

        current_time = datetime.now()
        delta = (current_time - datetime.strptime(timestamp_action, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
        if command_type == "play":
            timestamp = timestamp + delta

        response_timestamp = CommandResponse(commandType="seeked", timestamp=timestamp)
        response_status = CommandResponse(commandType=command_type)

        return response_timestamp, response_status

    async def handle_chat_state(self, session: Session, websocket: WebSocket):
        key = f"{session.session_id}:message"
        try:
            chat_state = await self.cache_storage.lrange(key, -10, -1)
        except ConnectionError:
            logger.error("Redis is unavailable")
            return None
        if chat_state:
            return await self.process_chat_state(chat_state, session, websocket)
        return None

    async def process_chat_state(self, chat_state: list, session: Session, websocket: WebSocket):
        return [message.decode("utf-8") for message in chat_state]

    async def save_message_to_cache(self, session: Session, response: MessageResponse):
        key = f"{session.session_id}:message"
        await self.cache_storage.rpush(key, response.json())

    async def save_command_to_cache(self, session: Session, data: dict):
        key = f"{session.session_id}:command"
        timestamp = data["timestamp"]
        command_type = data["commandType"]
        timestamp_action = str(datetime.now())

        if command_type in ["play", "pause"]:
            await self.cache_storage.hset(key, "commandType", command_type)
            await self.cache_storage.hset(key, "timestamp", timestamp)
            await self.cache_storage.hset(key, "timestamp_action", timestamp_action)
        elif command_type == "seeked":
            await self.cache_storage.hset(key, "timestamp", timestamp)
