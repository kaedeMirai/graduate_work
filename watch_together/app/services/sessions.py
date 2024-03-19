from uuid import UUID

from fastapi import HTTPException, status
from fastapi.logger import logger
from pymongo.errors import ServerSelectionTimeoutError

from watch_together.app.models import Session
from watch_together.app.db.provider import get_session_storage
from watch_together.app.api.v1.sessions.schemas import CreateSession

active_sessions = {}


async def get_active_sessions():
    return active_sessions


async def add_active_session(session: Session):
    active_sessions[session.session_id] = session


async def get_session(session_id: UUID) -> Session | str:
    logger.info("Get session with id: %s", session_id)
    session = active_sessions.get(session_id, None)
    if not session:
        storage = get_session_storage()
        session = await storage.get_session(session_id)
    return session


async def create_session(session_data: CreateSession, friends: list) -> Session:
    logger.info("Create new Session")
    session = Session(participants=session_data.selected_participants, friends=friends, movie_id=session_data.movie_id)
    storage = get_session_storage()
    try:
        await storage.save_session(session)
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MongoDB server is unavailable.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PROBLEMS: {ex}")
    logger.debug("Session with id: %s created", session.session_id)
    await add_active_session(session)
    return session
