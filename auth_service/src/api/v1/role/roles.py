from uuid import UUID

from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.v1.role.schemas import RoleCreate, RoleUpdate, RoleResponse
from services.role_service import RoleService, get_role_service
from services.user_roles_service import UserRoleService, get_user_roles_service, roles_required
from exceptions.exceptions import EntityNotFoundException, DuplicateEntityException
from opentelemetry import trace


tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/role", tags=["roles"])

oauth2_scheme = HTTPBearer()


@router.post(
    "/create",
    response_model=RoleResponse,
    summary="Create a role",
    description="Creating a role, specifying a unique name and \
                 selecting permissions from the list of existing ones.",
)
async def create_role(
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> RoleResponse:
    with tracer.start_as_current_span("create_role"):
        try:
            response = await role_service.create_role(role_data, auth_credentials.credentials)
            return response
        except EntityNotFoundException:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The permission was not found")
        except DuplicateEntityException as ex:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ex))


@router.get(
    "/read/{role_id}", response_model=RoleResponse, summary="Viewing a role", description="Viewing a role by id."
)
async def read_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> RoleResponse:
    with tracer.start_as_current_span("read_role_span"):
        try:
            response = await role_service.read_role(role_id, auth_credentials.credentials)
            return response
        except EntityNotFoundException:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The role was not found")


@router.put(
    "/update/{role_id}",
    response_model=RoleResponse,
    summary="Update the role.",
    description="Role update: changing the name and list of permissions for a role by role id.",
)
@roles_required("admin")
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    role_service: RoleService = Depends(get_role_service),
    user_role_service: UserRoleService = Depends(get_user_roles_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> RoleResponse:
    with tracer.start_as_current_span("update_role"):
        try:
            response = await role_service.update_role(role_id, role_data, auth_credentials.credentials)
            return response
        except EntityNotFoundException as ex:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
        except DuplicateEntityException as ex:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ex))


@router.delete(
    "/delete/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a role.",
    description="Deleting a role by a unique id, if such a role exists.",
)
@roles_required("admin")
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    user_role_service: UserRoleService = Depends(get_user_roles_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("delete_role"):
        try:
            response = await role_service.delete_role(role_id, auth_credentials.credentials)
            return response
        except EntityNotFoundException:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The role was not found")


@router.get(
    "/permissions", summary="View all permissions.", description="View all permissions that exist in the database."
)
async def get_all_permissions(
    role_service: RoleService = Depends(get_role_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("get_all_permissions_span"):
        try:
            response = await role_service.get_all_permissions(auth_credentials.credentials)
            return response
        except EntityNotFoundException:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The permission was not found")
