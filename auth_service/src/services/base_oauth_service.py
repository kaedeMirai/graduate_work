from enum import Enum
from abc import ABC, abstractmethod

from httpx import AsyncClient
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service import UserService


class BaseOauthService(ABC):
    provider_name: str

    def __init__(self, session: AsyncSession, base_url: str):
        self.client = AsyncClient(base_url=base_url)
        self.user_service = UserService(session)

    @abstractmethod
    async def process_user_data(self, response_json):
        pass

    @abstractmethod
    async def get_user(self, token: str):
        headers = {"Authorization": f"OAuth {token}"}
        response = await self.client.get(
            headers=headers,
            url=self.get_user_url(),
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Request {self.__class__.__name__} failed. Error: {response.text}",
            )
        return await self.process_user_data(response)

    @abstractmethod
    def get_user_url(self) -> str:
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass
