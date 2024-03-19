from uuid import UUID
from pydantic import BaseModel


class SocialAccountSchema(BaseModel):
    user_id: UUID
    social_id: str
    social_email: str
    social_name: str
