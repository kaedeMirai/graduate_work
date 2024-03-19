import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import create_user_cm


@pytest_asyncio.fixture(scope="function")
async def simple_user(session: AsyncSession):
    async with create_user_cm(
        session=session,
        username="simple_user_login",
        password="simple_user_password",
        first_name="simple_user_name",
        last_name="simple_user_last_name",
    ) as user:
        yield user
