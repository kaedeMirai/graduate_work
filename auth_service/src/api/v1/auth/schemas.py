from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str


class UserInDb(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    id: str
    username: str
    roles: list


class AuthUserResponse(AuthUser):
    first_name: str
    last_name: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class LoginResponse(Token):
    user_id: str


class LoginHistory(BaseModel):
    user_id: str
    user_agent: str | None = None
    date_auth: datetime

    class Config:
        orm_mode = True


class NewUsername(BaseModel):
    username: str


class NewPassword(BaseModel):
    password: str


class FriendResponse(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
