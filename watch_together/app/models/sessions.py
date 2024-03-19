from uuid import uuid4, UUID
from typing import List, Dict
from fastapi import WebSocket

from pydantic import Field, BaseModel


class Session(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    clients: List[WebSocket] = Field(default=[])
    friends: List[Dict[str, str]] = Field(default=[])
    movie_id: str = Field(default="")
    participant: List[str] = Field(default=[])

    class Config:
        arbitrary_types_allowed = True
