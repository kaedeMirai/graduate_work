import httpx
from fastapi import Depends, HTTPException, status
from fastapi.logger import logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from watch_together.app.config import settings
from watch_together.app.api.v1.sessions.schemas import AuthUserResponse

oauth2_scheme = HTTPBearer()


async def get_current_user(auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        async with httpx.AsyncClient() as client:
            url = settings.verify_token_url
            headers = {"Authorization": f"Bearer {auth_credentials.credentials}"}
            response = await client.get(url=url, headers=headers)
            auth_user_data = response.json()
            user_data = AuthUserResponse(**auth_user_data)
            logger.info("User authenticated successfully: %s", user_data.username)
            return user_data
    except httpx.HTTPError:
        logger.error("Could not validate credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


async def get_user_friends(auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        async with httpx.AsyncClient() as client:
            url = settings.get_user_friends_url
            headers = {"Authorization": f"Bearer {auth_credentials.credentials}"}
            response = await client.get(url, headers=headers)
            friends_list = response.json()
            return friends_list
    except httpx.HTTPError:
        logger.error("Could not validate credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
