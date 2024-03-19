from uuid import UUID
from watch_together.app.models import Session
from watch_together.app.db.mongo import get_mongodb_client


class SessionStorageProvider:

    def __init__(self, client):
        self.client = client

    async def get_session(self, session_id: UUID) -> Session:
        return await self.client.get_session(session_id)

    async def save_session(self, session: Session) -> str:
        return await self.client.save_session(session)


def get_session_storage() -> SessionStorageProvider:
    return SessionStorageProvider(client=get_mongodb_client())
