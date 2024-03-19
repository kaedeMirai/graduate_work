import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, Depends, HTTPException, WebSocketDisconnect, status
from fastapi.logger import logger
from redis.asyncio import Redis
from pymongo.errors import ServerSelectionTimeoutError

from watch_together.app.config import settings
from watch_together.app.services import sessions
from watch_together.app.services.sessions import get_session
from watch_together.app.services.websocket import ConnectionManager
from watch_together.app.db.cache.redis_cache import RedisCacheStorage
from watch_together.app.utils.auth_util import get_current_user, get_user_friends
from watch_together.app.api.v1.sessions.schemas import SessionId, AuthUserResponse, CreateSession


router = APIRouter(prefix="/session", tags=["Session"])

manager = ConnectionManager(
    RedisCacheStorage(Redis(host=settings.redis_host, port=settings.redis_port)),
)


@router.get("/test")
async def test_session():
    return "App is healthy"


@router.post(
    "/create_session",
    response_model=SessionId,
    summary="Creating new Session",
)
async def create_session(
    session_data: CreateSession,
    current_user: AuthUserResponse = Depends(get_current_user),
    user_friends=Depends(get_user_friends),
):
    try:
        current_user_dict = current_user.dict()
        friends = user_friends + [current_user_dict]
        session = await sessions.create_session(session_data, friends)
        return session
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MongoDB server is unavailable.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Session creation error: {ex}")


@router.get("/get_friends", summary="Get user friends")
async def get_friends(friends_list=Depends(get_user_friends)):
    return {"friends": friends_list}


@router.get("/view_sessions")
async def view_sessions():
    session = await sessions.get_active_sessions()
    return str(session)


@router.websocket("/ws/join_session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: UUID):
    session = await get_session(session_id=session_id)
    if not session:
        await websocket.close(code=status.HTTP_404_NOT_FOUND, reason=f"Session with session_id {session_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with session_id {session_id} not found"
        )
    try:
        await manager.connect(session, websocket)
    except ConnectionError:
        logger.error("Redis is unavailable")
    try:
        while True:
            logger.info("trying to receive message")
            receive_data = await websocket.receive_text()  # noqa: F841
            logger.info(f"received: {receive_data}")

            data = json.loads(receive_data)

            await manager.handle_message(data, session, websocket)

    except WebSocketDisconnect:
        await manager.disconnect(session, websocket)
    except ConnectionError:
        logger.error("Redis is unavailable")
