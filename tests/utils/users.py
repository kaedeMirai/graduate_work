from watch_together.app.api.v1.sessions.schemas import AuthUserResponse


async def get_user_test() -> AuthUserResponse:
    return AuthUserResponse(id="1", username="test", first_name="test", last_name="test")


async def get_user_friends_test() -> list[dict]:
    return [
        {"id": "2", "username": "test2", "first_name": "test2", "last_name": "test2"},
        {"id": "3", "username": "test3", "first_name": "test3", "last_name": "test3"},
    ]
