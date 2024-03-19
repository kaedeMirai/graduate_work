from sqlalchemy import Column, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, BaseModel

rolepermissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, index=True, unique=True)
    permissions = relationship("Permission", secondary=rolepermissions, back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role", cascade="all,delete")


class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String, index=True)
    roles = relationship("Role", secondary=rolepermissions, back_populates="permissions")


class UserRole(BaseModel):
    __tablename__ = "user_role"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True, nullable=False)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="_user_role_uc"),)

    def __repr__(self) -> str:
        return f"<User id: {self.user_id}>"
