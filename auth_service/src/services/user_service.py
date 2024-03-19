from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash
from opentelemetry import trace

from api.v1.auth.schemas import UserLogin, UserCreate
from exceptions.exceptions import AuthorizationException, DuplicateEntityException, EntityNotFoundException
from models.user import AuthHistory, AuthSessions, User, SocialAccount
from models.utils import SocialAccountSchema
from models.role import Role, Permission, UserRole

tracer = trace.get_tracer(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_dto: UserCreate):
        with tracer.start_as_current_span("UserService.create_user"):
            if await self._get_user_by_username(user_dto.username):
                raise DuplicateEntityException

            user = User(**user_dto.model_dump())

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            default_role = await self._get_default_role("user")

            if default_role:
                user_role = UserRole(user_id=user.id, role_id=default_role.id)
                self.session.add(user_role)
                await self.session.commit()

            return user

    async def reset_username(self, user_id: str, new_username: str):
        with tracer.start_as_current_span("UserService.reset_username"):
            if await self._get_user_by_username(new_username):
                raise DuplicateEntityException

            user = await self._get_user_by_id(user_id)
            setattr(user, "username", new_username)
            await self.session.commit()

    async def reset_password(self, user_id: str, new_password: str):
        with tracer.start_as_current_span("UserService.reset_password"):
            user = await self._get_user_by_id(user_id)
            setattr(user, "password", generate_password_hash(new_password))
            await self.session.commit()

    async def get_login_history(self, user_id: str) -> list[dict]:
        with tracer.start_as_current_span("UserService.get_login_history"):
            history = await self.session.scalars(select(AuthHistory).where(AuthHistory.user_id == user_id))

            return [auth.as_dict() for auth in history.all()]

    async def add_auth_session(self, user_id: str, tokens: dict):
        with tracer.start_as_current_span("UserService.add_auth_session"):
            auth_session = AuthSessions(
                user_id=user_id, access_token=tokens.get("access_token"), refresh_token=tokens.get("refresh_token")
            )

            self.session.add(auth_session)
            await self.session.commit()
            await self.session.refresh(auth_session)

    async def add_auth_history(self, user_id: str, user_agent: str):
        with tracer.start_as_current_span("UserService.add_auth_history"):
            auth_history = AuthHistory(user_id=user_id, user_agent=user_agent)
            self.session.add(auth_history)
            await self.session.commit()
            await self.session.refresh(auth_history)

    async def get_auth_session_by_token(self, token: str) -> AuthSessions:
        with tracer.start_as_current_span("UserService.get_auth_session_by_token"):
            auth_session = await self.session.scalar(
                select(AuthSessions).where((AuthSessions.access_token == token) | (AuthSessions.refresh_token == token))
            )

            return auth_session

    async def check_credentials(self, user_dto: UserLogin):
        with tracer.start_as_current_span("UserService.check_credentials"):
            user = await self._get_user_by_username(user_dto.username)

            if not user:
                raise EntityNotFoundException

            if not await user.check_password(user_dto.password):
                raise AuthorizationException

            return user

    async def check_social_accounts(self, social_name: str, social_id: str):
        social_account = await self.session.scalar(
            select(SocialAccount).where(
                and_(
                    SocialAccount.social_name == social_name,
                    SocialAccount.social_id == social_id,
                )
            )
        )
        if social_account:
            return await self._get_user_by_id(user_id=social_account.user_id)
        else:
            return None

    async def create_social_account(self, social_account_dto: SocialAccountSchema) -> SocialAccount:
        if await self.check_social_accounts(social_account_dto.social_name, social_account_dto.social_id):
            raise DuplicateEntityException

        social_account = SocialAccount(**social_account_dto.model_dump())
        self.session.add(social_account)
        await self.session.commit()
        await self.session.refresh(social_account)

        return social_account

    async def get_user_with_roles(self, user_id: str) -> dict:
        try:
            user_data = await self.session.execute(
                select(User).options(joinedload(User.user_roles).joinedload(UserRole.role)).where(User.id == user_id)
            )

            user = user_data.scalar()
            role_names = [item.role.name for item in user.user_roles]

            return {
                "id": str(user.id),
                "username": user.username,
                "roles": role_names,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        except NoResultFound:
            raise EntityNotFoundException

    async def get_all_users(self, user_id: str) -> dict:
        try:
            users = await self.session.scalars(select(User).limit(10).where(User.id != user_id))
            friends = users.all()
            return {"friends": friends}
        except NoResultFound:
            raise EntityNotFoundException

    async def _get_user_by_id(self, user_id: str) -> User | None:
        with tracer.start_as_current_span("UserService._get_user_by_id"):
            try:
                user = await self.session.scalar(select(User).where(User.id == user_id))
                return user
            except NoResultFound:
                return None

    async def _get_user_by_username(self, username: str) -> User | None:
        with tracer.start_as_current_span("UserService._get_user_by_username"):
            try:
                user = await self.session.scalar(select(User).where(User.username == username))
                return user
            except NoResultFound:
                return None

    async def _get_default_role(self, role_name="user"):
        with tracer.start_as_current_span("UserService._get_default_role"):
            default_role = await self.session.scalar(select(Role).filter(Role.name == role_name))

            if not default_role:
                default_role = await self._create_default_role(role_name)

            return default_role

    async def _create_default_role(self, role_name: str, permissions_names=["edit", "rewrite"]):
        permissions = await self._get_permissions_for_default_role(permissions_names)

        default_role = Role(name=role_name, permissions=permissions)
        self.session.add(default_role)
        await self.session.commit()

        return default_role

    async def _get_permissions_for_default_role(self, permission_names: list):
        permissions = []
        for permission_name in permission_names:
            permission = await self.session.scalar(select(Permission).filter(Permission.name == permission_name))
            if not permission:
                permission = await self._create_permissions_for_default_role(permission_name)
            permissions.append(permission)

        return permissions

    async def _create_permissions_for_default_role(self, permission_name: str):
        permission = Permission(name=permission_name)
        self.session.add(permission)
        await self.session.commit()

        return permission
