import asyncio
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import settings
from models.user import User
from exceptions.exceptions import DuplicateEntityException


async def create_super_user():
    username = input("Please enter username: ")
    password = input("Please provide password: ")
    first_name = input("Please provide first name: ")
    last_name = input("Please provide last name: ")

    dsn = settings.build_db_connection_uri()

    engine = create_async_engine(url=dsn, echo=True, future=True)
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    user_data = {"username": username, "password": password, "first_name": first_name, "last_name": last_name}
    try:
        print("Creating superuser ...")
        async with async_session() as session:
            await create_user(session, user_data)
    except DBAPIError:
        print("There was an error while creating superuser. Please try again.")
    else:
        print("Superuser was successfully created")


async def create_user(session: AsyncSession, user_data):
    user = await session.scalar(select(User).where(User.username == user_data["username"]))

    if user:
        raise DuplicateEntityException

    user = User(
        username=user_data["username"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        is_super_user=True,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


if __name__ == "__main__":
    asyncio.run(create_super_user())
