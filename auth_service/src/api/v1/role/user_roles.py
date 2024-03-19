from uuid import UUID

from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.v1.role.schemas import RolePermissionsResponse, DeleteRoleResponse, UserRoleResponse
from services.user_roles_service import UserRoleService, get_user_roles_service
from exceptions.exceptions import EntityNotFoundException, DuplicateEntityException
from opentelemetry import trace


tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/user-role", tags=["user_roles"])

oauth2_scheme = HTTPBearer()


@router.post(
    "/{user_id}/roles",
    response_model=UserRoleResponse,
    summary="Assign a role to a user.",
    description="Assigning a role to a user, if such a role exists and the user does not have this role.",
)
async def assign_role_to_user(
    user_id: UUID,
    role_id: UUID,
    user_role_service: UserRoleService = Depends(get_user_roles_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("assign_role_to_user"):
        try:
            response = await user_role_service.assign_user_to_role(user_id, role_id, auth_credentials.credentials)
            return response
        except DuplicateEntityException:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this role already exists")
        except EntityNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The role or user was not found"
            )


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=DeleteRoleResponse,
    summary="Removing a role from a user.",
    description="Deleting a role from a user, by user id and role id, if this role belongs to the user.",
)
async def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    user_role_service: UserRoleService = Depends(get_user_roles_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("remove_role_from_user"):
        try:
            response = await user_role_service.remove_role_from_user(user_id, role_id, auth_credentials.credentials)
            return {"message": "Role deleted successfully", "role": response.role.name, "user": response.user.username}
        except EntityNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The role or user was not found"
            )


@router.get(
    "/{user_id}/permissions",
    response_model=RolePermissionsResponse,
    summary="Viewing user permissions.",
    description="Checking which permissions are available to the user, depending on their inherent roles.",
)
async def check_user_permissions(
    user_id: UUID,
    user_role_service: UserRoleService = Depends(get_user_roles_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("check_user_permissions"):
        try:
            response = await user_role_service.check_user_permissions(user_id, auth_credentials.credentials)
            return response
        except EntityNotFoundException as ex:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
