from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


@asynccontextmanager
async def create_user_cm(session: AsyncSession, **kwargs) -> User:
    u = User(**kwargs)
    session.add(u)
    await session.commit()
    await session.refresh(u)
    yield u
    await session.delete(u)
    await session.commit()
