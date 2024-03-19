from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.schemas import UserCreate, UserLogin
from models.user import User
from db.cache.abstract_cache import AbstractCacheStorage
from db.cache.redis_cache import get_cache
from db.postgres import get_session
from exceptions.exceptions import AuthorizationException
from services.user_service import UserService
from services.token_utils import TokenUtil


class AuthService:
    def __init__(self, cache: AbstractCacheStorage, session: AsyncSession):
        self.token_util = TokenUtil(cache)
        self.user_service = UserService(session)

    async def register(self, user: UserCreate) -> User:
        return await self.user_service.create_user(user)

    async def login(self, user_dto: UserLogin, user_agent: str) -> dict:
        user = await self.user_service.check_credentials(user_dto)

        tokens = self.token_util.create_tokens(base_payload={"sub": str(user.id)})

        await self.user_service.add_auth_session(user.id, tokens)
        await self.user_service.add_auth_history(user.id, user_agent)

        return tokens, user.id

    async def logout(self, access_token: str):
        payload = await self.token_util.validate_access_token(access_token)

        if not payload:
            raise AuthorizationException

        auth_session = await self.user_service.get_auth_session_by_token(access_token)
        await self.token_util.revoke_token(auth_session.access_token)
        await self.token_util.revoke_token(auth_session.refresh_token)

    async def get_login_history(self, access_token: str) -> list[dict]:
        payload = await self.token_util.validate_access_token(access_token)

        if not payload:
            raise AuthorizationException

        return await self.user_service.get_login_history(payload.get("sub"))

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = await self.token_util.validate_refresh_token(refresh_token)

        if not payload:
            raise AuthorizationException

        auth_session = await self.user_service.get_auth_session_by_token(refresh_token)
        await self.token_util.revoke_token(auth_session.access_token)
        await self.token_util.revoke_token(auth_session.refresh_token)

        tokens = self.token_util.create_tokens(base_payload={"sub": payload.get("sub")})
        await self.user_service.add_auth_session(payload.get("sub"), tokens)

        return tokens

    async def reset_password(self, new_password: str, access_token: str):
        payload = await self.token_util.validate_access_token(access_token)

        if not payload:
            raise AuthorizationException

        await self.user_service.reset_password(payload.get("sub"), new_password)

    async def reset_username(self, new_username: str, access_token: str):
        payload = await self.token_util.validate_access_token(access_token)

        if not payload:
            raise AuthorizationException

        await self.user_service.reset_username(payload.get("sub"), new_username)

    async def verify_access_token(self, access_token: str):
        payload = await self.token_util.validate_access_token(access_token)

        if not payload:
            raise AuthorizationException

        return await self.user_service.get_user_with_roles(payload.get("sub"))

    async def verify_user_credentials(self, user_dto: UserLogin):
        user = await self.user_service.check_credentials(user_dto)
        return await self.user_service.get_user_with_roles(user.id)

    async def get_friends(self, access_token: str):
        payload = await self.token_util.validate_access_token(access_token)

        if not payload:
            raise AuthorizationException

        return await self.user_service.get_all_users(payload.get("sub"))


def get_auth_service(cache: AbstractCacheStorage = Depends(get_cache), session: AsyncSession = Depends(get_session)):
    return AuthService(cache, session)
