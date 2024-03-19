from uuid import UUID
from functools import wraps

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from opentelemetry import trace

from db.postgres import get_session
from db.cache.redis_cache import get_cache
from db.cache.abstract_cache import AbstractCacheStorage
from models.user import User
from models.role import UserRole, Role
from services.token_utils import TokenUtil
from exceptions.exceptions import AuthorizationException, EntityNotFoundException, DuplicateEntityException

tracer = trace.get_tracer(__name__)


class UserRoleService:
    def __init__(self, cache: AbstractCacheStorage, db_session: AsyncSession):
        self.token_util = TokenUtil(cache)
        self.db_session = db_session

    async def get_roles_current_user(self, access_token: str) -> User:
        with tracer.start_as_current_span("get_roles_current_user"):
            payload = await self.token_util.validate_access_token(access_token)
            user_id = payload.get("sub")

            if not payload:
                raise AuthorizationException

            with tracer.start_as_current_span("get_roles_current_user"):
                user_data = await self.db_session.execute(
                    select(User)
                    .options(joinedload(User.user_roles).joinedload(UserRole.role))
                    .where(User.id == user_id)
                )
            user = user_data.scalar()
            role_names = [item.role.name for item in user.user_roles]
            return role_names

    async def assign_user_to_role(self, user_id: UUID, role_id: UUID, access_token: str):
        with tracer.start_as_current_span("assign_user_to_role"):
            payload = await self.token_util.validate_access_token(access_token)

            if not payload:
                raise AuthorizationException
            with tracer.start_as_current_span("query_user_and_role"):
                user = await self.db_session.scalar(
                    select(User).options(joinedload(User.user_roles)).where(User.id == user_id)
                )
                role = await self.db_session.get(Role, role_id)

            if not user or not role:
                raise EntityNotFoundException

            with tracer.start_as_current_span("check_existing_user_role"):
                if any(user_role.role_id == role_id for user_role in user.user_roles):
                    raise DuplicateEntityException

            with tracer.start_as_current_span("add_user_to_role_commit"):
                user_roles = UserRole(user=user, role=role)
                self.db_session.add(user_roles)
                await self.db_session.commit()

            return user_roles

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID, access_token: str):
        with tracer.start_as_current_span("remove_role_from_user"):
            payload = await self.token_util.validate_access_token(access_token)

            if not payload:
                raise AuthorizationException

            with tracer.start_as_current_span("query_user_and_role"):
                user = await self.db_session.get(User, user_id)
                role = await self.db_session.get(Role, role_id)

            if not user or not role:
                raise EntityNotFoundException

            with tracer.start_as_current_span("query_user_roles"):
                user_roles = await self.db_session.scalar(
                    select(UserRole).filter(UserRole.user == user, UserRole.role == role)
                )

            if not user_roles:
                raise EntityNotFoundException

            with tracer.start_as_current_span("delete_user_roles_commit"):
                await self.db_session.delete(user_roles)
                await self.db_session.commit()

            return user_roles

    async def check_user_permissions(self, user_id: UUID, access_token: str) -> dict[list[str], list[str]]:
        with tracer.start_as_current_span("check_user_permissions"):
            payload = await self.token_util.validate_access_token(access_token)

            if not payload:
                raise AuthorizationException

            with tracer.start_as_current_span("query_user_data"):
                user = await self.db_session.execute(
                    select(User)
                    .options(joinedload(User.user_roles).joinedload(UserRole.role).joinedload(Role.permissions))
                    .where(User.id == user_id)
                )
                user = user.scalar()

            if not user:
                raise EntityNotFoundException("User not found")

            with tracer.start_as_current_span("process_user_data"):
                role_names = [item.role.name for item in user.user_roles]
                permission_names = list(set(p.name for ur in user.user_roles for p in ur.role.permissions))

            if not permission_names:
                raise EntityNotFoundException("Role not found")

            return {"role_names": role_names, "permission_names": permission_names}


def get_user_roles_service(
    cache: AbstractCacheStorage = Depends(get_cache), db_session: AsyncSession = Depends(get_session)
) -> UserRoleService:
    return UserRoleService(cache, db_session)


def roles_required(required_role: str):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user_role_service: UserRoleService = kwargs.get("user_role_service")
            auth_credentials = kwargs.get("auth_credentials")
            roles = await user_role_service.get_roles_current_user(auth_credentials.credentials)
            if required_role not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
            return await function(*args, **kwargs)

        return wrapper

    return decorator
