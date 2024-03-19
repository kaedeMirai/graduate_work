from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from sqlalchemy.orm import declarative_base
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
Base = declarative_base()

dsn = settings.build_db_connection_uri()

engine = create_async_engine(url=dsn, echo=True, future=True)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    with tracer.start_as_current_span("get_db_session_span"):
        async with async_session() as session:
            yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
