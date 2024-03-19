import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from alembic.config import Config as AlembicConfig

from core.config import Settings
from db.postgres import Base


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def session_engine(settings: Settings):
    engine = create_async_engine(url=settings.build_db_connection_uri(), echo=True, future=True)
    # TODO: setup and teardown should be change after alembic
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pass
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def sessionmaker(session_engine: AsyncEngine):
    yield async_sessionmaker(
        bind=session_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
    )


@pytest_asyncio.fixture(scope="session")
async def session(sessionmaker: async_sessionmaker[AsyncSession]):
    try:
        session: AsyncSession = sessionmaker()
        yield session
    finally:
        await session.close()
