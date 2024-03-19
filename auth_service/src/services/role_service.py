from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from opentelemetry import trace

from db.postgres import get_session
from db.cache.redis_cache import get_cache
from db.cache.abstract_cache import AbstractCacheStorage
from models.role import Role, Permission
from services.token_utils import TokenUtil
from exceptions.exceptions import AuthorizationException, EntityNotFoundException, DuplicateEntityException
from api.v1.role.schemas import RoleCreate, RoleUpdate, RoleResponse

tracer = trace.get_tracer(__name__)


class RoleService:
    def __init__(self, cache: AbstractCacheStorage, db_session: AsyncSession):
        self.token_util = TokenUtil(cache)
        self.db_session = db_session

    async def create_role(self, role_data: RoleCreate, access_token: str) -> RoleResponse:
        with tracer.start_as_current_span("create_role"):
            await self._validate_access_token(access_token)

            with tracer.start_as_current_span("check_existing_role"):
                existing_role = await self.db_session.execute(select(Role).where(Role.name == role_data.name))
                if existing_role.scalar():
                    raise DuplicateEntityException(f'Role with name "{role_data.name}" already exists')

                new_role = Role(name=role_data.name)

                for permission_name in role_data.permission_names:
                    with tracer.start_as_current_span("check_permission"):
                        permission_result = await self.db_session.execute(
                            select(Permission).where(Permission.name == permission_name)
                        )
                        permission = permission_result.scalar()
                        if not permission:
                            raise EntityNotFoundException

                        new_role.permissions.append(permission)
                with tracer.start_as_current_span("add_session_commit_refresh"):
                    self.db_session.add(new_role)
                    await self.db_session.commit()
                    await self.db_session.refresh(new_role)

                return RoleResponse(id=new_role.id, name=new_role.name, permission_names=role_data.permission_names)

    async def read_role(self, role_id: UUID, access_token: str):
        with tracer.start_as_current_span("read_role"):
            await self._validate_access_token(access_token)

            with tracer.start_as_current_span("query_role_data"):
                role_data = await self.db_session.scalars(
                    select(Role).options(joinedload(Role.permissions)).filter(Role.id == role_id)
                )

            role_data_list = list(role_data.unique())
            if not role_data_list:
                raise EntityNotFoundException

            role_data = role_data_list[0]

            if not role_data:
                raise EntityNotFoundException
            return RoleResponse(
                id=role_data.id,
                name=role_data.name,
                permission_names=[permission.name for permission in role_data.permissions],
            )

    async def update_role(self, role_id: UUID, role_data: RoleUpdate, access_token: str):

        await self._validate_access_token(access_token)

        role = await self._query_role(role_id)

        await self._update_role_name(role, role_data)
        await self._update_role_permissions(role, role_data)

        await self._commit_and_refresh(role)

        role_to_update = {
            "id": role.id,
            "name": role.name,
            "permission_names": (
                role_data.permission_names
                if role_data.permission_names is not None
                else [permission.name for permission in role.permissions]
            ),
        }
        return role_to_update

    async def delete_role(self, role_id: UUID, access_token: str):
        with tracer.start_as_current_span("delete_role"):
            await self._validate_access_token(access_token)

            with tracer.start_as_current_span("query_role"):
                role = await self.db_session.execute(select(Role).where(Role.id == role_id))
                role = role.scalar()

            if role is None:
                raise EntityNotFoundException
            with tracer.start_as_current_span("delete_role_commit"):
                await self.db_session.delete(role)
                await self.db_session.commit()

            return {"message": f"Role {role.name} successfully deleted"}

    async def get_all_permissions(self, access_token: str):
        payload = await self.token_util.validate_access_token(access_token)

        if not payload:
            raise AuthorizationException

        response = await self.db_session.execute(select(Permission))
        permissions = response.scalars().all()

        if not permissions:
            raise EntityNotFoundException
        return {"permissions": permissions}

    async def _validate_access_token(self, access_token: str):
        with tracer.start_as_current_span("validate_access_token"):
            payload = await self.token_util.validate_access_token(access_token)
            if not payload:
                raise AuthorizationException
            return payload

    async def _query_role(self, role_id: UUID):
        with tracer.start_as_current_span("query_role"):
            role = await self.db_session.scalar(
                select(Role).options(joinedload(Role.permissions)).where(Role.id == role_id)
            )
        if role is None:
            raise EntityNotFoundException("The role was not found")
        return role

    async def _update_role_name(self, role, role_data: RoleUpdate):
        with tracer.start_as_current_span("update_role_name"):
            if role_data.name is not None:
                await self._get_existing_role_by_name(role_data.name, role.id)
                role.name = role_data.name

    async def _get_existing_role_by_name(self, name, current_role_id):
        existing_role = await self.db_session.execute(
            select(Role).where(Role.name == name).where(Role.id != current_role_id)
        )
        return existing_role.scalar()

    async def _update_role_permissions(self, role, role_data: RoleUpdate):
        with tracer.start_as_current_span("update_role_permissions"):
            if role_data.permission_names is not None:
                permissions = await self._get_permissions_by_names(role_data.permission_names)
                role.permissions.clear()
                for permission_name in role_data.permission_names:
                    permission = next((p for p in permissions if p.name == permission_name), None)
                    if not permission:
                        raise EntityNotFoundException("The permission was not found")
                    role.permissions.append(permission)

    async def _get_permissions_by_names(self, permission_names):
        permission_results = await self.db_session.execute(
            select(Permission).where(Permission.name.in_(permission_names))
        )
        return permission_results.scalars().all()

    async def _commit_and_refresh(self, role):
        with tracer.start_as_current_span("commit_and_refresh"):
            await self.db_session.commit()
            await self.db_session.refresh(role)


def get_role_service(
    cache: AbstractCacheStorage = Depends(get_cache), db_session: AsyncSession = Depends(get_session)
) -> RoleService:
    return RoleService(cache, db_session)
