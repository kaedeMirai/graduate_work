from sqlalchemy import select

from models.base import Base
from models.user import User
from db.postgres import engine, async_session
from mock_data.data import test_users


async def create_test_users():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as client:
        for user_data in test_users:
            username = user_data["username"]
            password = user_data["password"]
            first_name = user_data["first_name"]
            last_name = user_data["last_name"]

            existing_user = await client.execute(select(User).where(User.username == username))
            if existing_user.scalar() is not None:
                continue

            user = User(username=username, password=password, first_name=first_name, last_name=last_name)
            client.add(user)

        await client.commit()
