from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.postgres import get_session
from api.v1.auth.schemas import UserCreate
from models.user import SocialNames
from models.utils import SocialAccountSchema
from exceptions.exceptions import EntityNotFoundException
from services.utils import send_temp_password_at_email, generate_random_string
from services.base_oauth_service import BaseOauthService


class YandexOauthService(BaseOauthService):

    provider_name = SocialNames.YANDEX.value
    base_url = "https://login.yandex.ru"

    async def process_user_data(self, response):
        yandex_user_social_id = response.json()["id"]

        user = await self.user_service.check_social_accounts(
            social_name=SocialNames.YANDEX.value, social_id=yandex_user_social_id
        )
        if user:
            return user

        user_dto = UserCreate(
            username=response.json()["login"],
            password=await generate_random_string(),
            first_name=response.json()["first_name"],
            last_name=response.json()["last_name"],
        )
        user = await self.user_service.create_user(user_dto)
        social_account_dto = SocialAccountSchema(
            user_id=user.id,
            social_id=yandex_user_social_id,
            social_email=response.json()["default_email"],
            social_name=SocialNames.YANDEX.value,
        )
        social_account = await self.user_service.create_social_account(social_account_dto)
        await send_temp_password_at_email(social_account.social_email, user_dto.password)
        return user

    async def get_user(self, token: str):
        return await super().get_user(token)

    def get_user_url(self):
        return f"/info?format=json&jwt_secret={settings.yandex_secret_id}"

    def get_provider_name(self):
        return self.provider_name


class OauthServiceProvider:
    def __init__(self):
        self.yandex_oauth_service = YandexOauthService


def get_oauth_service(provider_name: str, session: AsyncSession = Depends(get_session)) -> BaseOauthService:
    oauth_service = getattr(OauthServiceProvider(), f"{provider_name}_oauth_service", None)
    if not oauth_service:
        raise EntityNotFoundException
    return oauth_service(session, oauth_service.base_url)
