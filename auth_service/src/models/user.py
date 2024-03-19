import enum
import pydantic
from uuid import UUID
from datetime import datetime

from sqlalchemy import DateTime, Boolean, Text
from sqlalchemy.orm import backref
from sqlalchemy_utils import ChoiceType
from werkzeug.security import check_password_hash, generate_password_hash

from .base import BaseModel
from models.role import *


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))

    user_system_data = relationship("UserSystemData", uselist=False, back_populates="user", cascade="all,delete")
    auth_history = relationship("AuthHistory", back_populates="user", cascade="all,delete")
    user_roles = relationship("UserRole", back_populates="user", cascade="all,delete")
    user_sessions = relationship("AuthSessions", back_populates="user", cascade="all,delete")

    # friendships = relationship('Friendship', back_populates='user', cascade="all,delete")
    # friendships_as_friend = relationship('Friendship', back_populates='friend', cascade="all,delete")

    def __init__(
        self, username: str, password: str, first_name: str, last_name: str, is_super_user=False, user_system_data=None
    ) -> None:
        self.username = username
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

        if user_system_data is None:
            user_system_data = UserSystemData()

        user_system_data.__setattr__("is_superuser", is_super_user)
        self.user_system_data = user_system_data

    async def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserSystemData(BaseModel):
    __tablename__ = "user_system_data"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, default=datetime.utcnow, nullable=True)
    date_joined = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="user_system_data", cascade="all,delete")

    def __repr__(self) -> str:
        return f"<User id {self.user_id}>"


class AuthHistory(BaseModel):
    __tablename__ = "authentication_history"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_agent = Column(String(500))
    date_auth = Column(DateTime, default=datetime.utcnow)
    other_info = Column(String(500))

    user = relationship("User", back_populates="auth_history", cascade="all,delete")

    def __repr__(self) -> str:
        return f"<User id {self.user_id}>"

    def as_dict(self):
        return {column.name: str(getattr(self, column.name)) for column in self.__table__.columns}


class AuthSessions(BaseModel):
    __tablename__ = "authentication_sessions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    access_token = Column(String(), unique=True)
    refresh_token = Column(String(), unique=True)

    user = relationship("User", back_populates="user_sessions", cascade="all,delete")


class SocialNames(enum.StrEnum):
    YANDEX = "yandex"


class SocialAccount(BaseModel):
    __tablename__ = "social_account"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship(User, backref=backref("social_accounts"))

    social_id = Column(Text, nullable=False)
    social_email = Column(Text, nullable=True)
    social_name = Column(ChoiceType(SocialNames), nullable=False)

    __table_args__ = (UniqueConstraint("social_id", "social_name", name="social_pk"),)

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"


# class FriendshipStatus(enum.StrEnum):
#     PENDING = 'pending'
#     ACCEPTED = 'accepted'
#     REJECTED = 'rejected'


# class Friendship(BaseModel):
#     __tablename__ = 'friendship'

#     user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
#     friend_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
#     status = Column(ChoiceType(FriendshipStatus), nullable=False)

#     user = relationship('User', back_populates='friendships', cascade="all,delete")
#     friend = relationship('User', foreign_keys='friendships_as_friend', cascade="all,delete")
