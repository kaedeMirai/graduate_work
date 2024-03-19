from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field


class SessionId(BaseModel):
    session_id: UUID
    participant: List[str] = []


class CreateSession(BaseModel):
    selected_participants: List[str] = []
    movie_id: str


class AuthUser(BaseModel):
    id: str
    username: str


class AuthUserResponse(AuthUser):
    first_name: str
    last_name: str


class AuthorResponse(BaseModel):
    id: str
    name: str


class MessageResponse(BaseModel):
    author: AuthorResponse
    message: str = ""
    id: UUID = Field(default_factory=uuid4)
    type: str = "message"
    timestamp: str = str(datetime.now())


class CommandResponse(BaseModel):
    type: str = "command"
    author_id: str | None = None
    commandType: str | None = None
    timestamp: float | None = None
