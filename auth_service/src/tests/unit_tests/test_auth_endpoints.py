from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.schemas import Token, UserInDb
from models.user import User


async def test_user_register(api_client: AsyncClient, session: AsyncSession, event_loop, request):
    user_data = {
        "username": "user_username",
        "password": "user_password",
        "first_name": "user_name",
        "last_name": "user_last_name",
    }

    result = await api_client.post("/api/v1/auth/register", json=user_data)

    user = await session.scalar(select(User).filter_by(username="user_username"))

    def delete_rows():
        async def afin():
            await session.delete(user)
            await session.commit()

        event_loop.run_until_complete(afin())

    request.addfinalizer(delete_rows)

    assert result.status_code == HTTPStatus.OK, f"{result.json()}"
    assert UserInDb(**result.json())


async def test_user_register_same_username(api_client: AsyncClient, session: AsyncSession, event_loop, request):
    user_data = {
        "username": "user_username",
        "password": "user_password",
        "first_name": "user_name",
        "last_name": "user_last_name",
    }
    await api_client.post("/api/v1/auth/register", json=user_data)
    result = await api_client.post("/api/v1/auth/register", json=user_data)

    user = await session.scalar(select(User).filter_by(username="user_username"))

    def delete_rows():
        async def afin():
            await session.delete(user)
            await session.commit()

        event_loop.run_until_complete(afin())

    request.addfinalizer(delete_rows)

    assert result.status_code == HTTPStatus.CONFLICT, f"{result.json()}"


async def test_login(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }

    result = await api_client.post("/api/v1/auth/login", json=login_data)

    assert result.status_code == HTTPStatus.OK, f"{result.json()}"
    assert Token(**result.json())


async def test_wrong_login(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username + "wrong_login",
        "password": "simple_user_password",
    }

    result = await api_client.post("/api/v1/auth/login", json=login_data)

    assert result.status_code == HTTPStatus.BAD_REQUEST, f"{result.json()}"


async def test_wrong_password(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "wrong_password",
    }

    result = await api_client.post("/api/v1/auth/login", json=login_data)

    assert result.status_code == HTTPStatus.UNAUTHORIZED, f"{result.json()}"


async def test_logout(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    token = result.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    result = await api_client.post("/api/v1/auth/logout", headers=headers)

    assert result.status_code == HTTPStatus.OK, f"{result.json()}"
    assert result.json() == "You're logged out"

    result = await api_client.post("/api/v1/auth/logout", headers=headers)
    assert result.status_code == HTTPStatus.UNAUTHORIZED, f"{result.json()}"


async def test_logout_via_refresh_token(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    token = result.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {token}"}

    result = await api_client.post("/api/v1/auth/logout", headers=headers)

    assert result.status_code == HTTPStatus.UNAUTHORIZED, f"{result.json()}"


async def test_refresh_token(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    token = result.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {token}"}

    result = await api_client.post("/api/v1/auth/refresh_token", headers=headers)

    assert result.status_code == HTTPStatus.OK, f"{result.json()}"
    assert Token(**result.json())


async def test_old_access_token_after_refresh(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    old_access_token = result.json()["access_token"]
    refresh_token = result.json()["refresh_token"]
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
    access_headers = {"Authorization": f"Bearer {old_access_token}"}
    await api_client.post("/api/v1/auth/refresh_token", headers=refresh_headers)

    result = await api_client.post("/api/v1/auth/logout", headers=access_headers)

    assert result.status_code == HTTPStatus.UNAUTHORIZED


async def test_login_history(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }
    await api_client.post("/api/v1/auth/login", json=login_data)
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    refresh_token = result.json()["refresh_token"]
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
    # refresh_token doesn't add new row at history
    result = await api_client.post("/api/v1/auth/refresh_token", headers=refresh_headers)
    access_token = result.json()["access_token"]
    access_headers = {"Authorization": f"Bearer {access_token}"}

    result = await api_client.get("/api/v1/auth/login_history", headers=access_headers)

    assert result.status_code == HTTPStatus.OK
    assert len(result.json()) == 2


async def test_reset_username(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    access_token = result.json()["access_token"]
    access_headers = {"Authorization": f"Bearer {access_token}"}
    new_username = {"username": "new_username"}

    result = await api_client.put(
        "/api/v1/auth/reset_username",
        headers=access_headers,
        json=new_username,
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json() == "Username was successfully changed to: username='new_username'"

    # Check that user can't use old username
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    assert result.status_code == HTTPStatus.BAD_REQUEST

    # Check that user can use new username
    login_data["username"] = "new_username"
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    assert result.status_code == HTTPStatus.OK


async def test_reset_password(api_client: AsyncClient, simple_user: User):
    user = simple_user
    login_data = {
        "username": user.username,
        "password": "simple_user_password",
    }
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    access_token = result.json()["access_token"]
    access_headers = {"Authorization": f"Bearer {access_token}"}
    new_password = {"password": "new_password"}

    result = await api_client.put(
        "/api/v1/auth/reset_password",
        headers=access_headers,
        json=new_password,
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json() == "Password was successfully changed"

    # Check that user can't use old password
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    assert result.status_code == HTTPStatus.UNAUTHORIZED

    # Check that user can use new password
    login_data["password"] = "new_password"
    result = await api_client.post("/api/v1/auth/login", json=login_data)
    assert result.status_code == HTTPStatus.OK
