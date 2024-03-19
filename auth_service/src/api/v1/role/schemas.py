from uuid import UUID
from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    permission_names: list[str]


class RoleResponse(BaseModel):
    id: UUID
    name: str | None = None
    permission_names: list[str] | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    permission_names: list[str] | None = None


class RolePermissionsResponse(BaseModel):
    role_names: list[str]
    permission_names: list[str]


class DeleteRoleResponse(BaseModel):
    message: str
    role: str
    user: str


class UserRoleResponse(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
