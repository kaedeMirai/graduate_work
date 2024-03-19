import uuid
from datetime import datetime, timedelta
from jose import JWTError, jwt
from opentelemetry import trace

from core.config import settings
from db.cache.abstract_cache import AbstractCacheStorage

tracer = trace.get_tracer(__name__)


class TokenUtil:
    TOKEN_TYPE_ACCESS = "access"
    TOKEN_TYPE_REFRESH = "refresh"

    # add type hints
    def __init__(self, cache: AbstractCacheStorage):
        self.cache = cache

    def create_tokens(self, base_payload: dict) -> dict:
        with tracer.start_as_current_span("TokenUtil.create_tokens"):
            access_token = self.create_token(
                base_payload, self.TOKEN_TYPE_ACCESS, timedelta(minutes=settings.access_token_expire_time)
            )
            refresh_token = self.create_token(
                base_payload, self.TOKEN_TYPE_REFRESH, timedelta(minutes=settings.refresh_token_expire_time)
            )

            return {"access_token": access_token, "refresh_token": refresh_token}

    def create_token(
        self, base_payload: dict, token_type: str, exp_timedelta: timedelta | None = timedelta(minutes=10)
    ) -> str:
        payload = base_payload.copy()

        jti = str(uuid.uuid4())
        exp = datetime.utcnow() + exp_timedelta
        payload.update({"jti": jti, "exp": exp, "type": token_type})

        return jwt.encode(payload, key=settings.auth_jwt_key, algorithm=settings.jwt_algorithm)

    async def validate_access_token(self, token: str) -> dict | None:
        return await self.validate_token(token, self.TOKEN_TYPE_ACCESS)

    async def validate_refresh_token(self, token: str) -> dict | None:
        return await self.validate_token(token, self.TOKEN_TYPE_REFRESH)

    async def validate_token(self, token: str, token_type: str) -> dict | None:
        with tracer.start_as_current_span("validate_token"):
            try:
                payload = jwt.decode(token, key=settings.auth_jwt_key, algorithms=[settings.jwt_algorithm])

                is_invalid_type = payload.get("type") != token_type
                is_revoked = await self._is_token_revoked(token)

                if is_invalid_type or is_revoked:
                    raise JWTError

                return payload
            except JWTError:
                return None

    async def revoke_token(self, token: str, exp: timedelta | int = timedelta(minutes=60)):
        with tracer.start_as_current_span("TokenUtil.revoke_token"):
            await self.cache.set(key=token, data=token, exp=exp)

    async def _is_token_revoked(self, token: str) -> bool:
        if await self.cache.get(token):
            return True

        return False
