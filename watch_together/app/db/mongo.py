from fastapi.logger import logger

from motor.motor_asyncio import AsyncIOMotorClient
from watch_together.app.config import get_settings, Settings
from watch_together.app.models import Session


class MongoClient:
    def __init__(self, settings: Settings):
        self.engine = AsyncIOMotorClient(settings.mongo_conn)

    async def init_db(self, db_name: str):
        self.engine.get_database(db_name)

    async def close_connection(self):
        self.engine.close()

    async def get_session(self, session_id) -> Session:
        db = self.engine.get_database("sessions")
        session_collection = db.get_collection(str(session_id))
        session = await session_collection.find_one({"_id": str(session_id)})
        logger.info("Get session from mongo: %s", session)
        return session

    async def save_session(self, session: Session) -> Session:
        db = self.engine.get_database("sessions")
        session_collection = db.get_collection(str(session.session_id))
        prep_session = session.model_dump(mode="json")
        prep_session["_id"] = str(session.session_id)
        saved_session = await session_collection.insert_one(prep_session)
        logger.info("Saved session to mongo: %s", saved_session)
        return session


def get_mongodb_client(settings: Settings = get_settings()) -> MongoClient:
    return MongoClient(settings)
