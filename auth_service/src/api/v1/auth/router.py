from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from opentelemetry import trace

from exceptions.exceptions import (
    DuplicateEntityException,
    EntityNotFoundException,
    AuthorizationException,
    INVALID_CREDENTIALS,
)
from services.auth_service import AuthService, get_auth_service
from services.providers_oauth_services import get_oauth_service
from services.base_oauth_service import BaseOauthService
from api.v1.auth.schemas import (
    UserInDb,
    UserCreate,
    UserLogin,
    Token,
    LoginHistory,
    NewUsername,
    NewPassword,
    FriendResponse,
    LoginResponse,
    AuthUserResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = HTTPBearer()

tracer = trace.get_tracer(__name__)


@router.post(
    "/register",
    response_model=UserInDb,
    summary="Register user",
    description="Creates new user with specified username and password if username is not already used",
)
async def register_user(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    with tracer.start_as_current_span("register_user"):
        try:
            response = await auth_service.register(user_data)
        except DuplicateEntityException:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already in use")
        return response


@router.post(
    "/oauth_redirect/{provider_name}",
    summary="For accepting oauth providers users",
    response_model=UserInDb,
)
async def oauth_redirect(
    access_token: str, expires_in: str, provider_name: str, oauth_service: BaseOauthService = Depends(get_oauth_service)
):
    with tracer.start_as_current_span("login"):
        response = await oauth_service.get_user(access_token)
        return response


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
    description="Returns access and refresh tokens if username and password are correct",
)
async def login(
    request: Request,
    form_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    with tracer.start_as_current_span("login"):
        user_agent = request.headers.get("user-agent")
        try:
            resp, user_id = await auth_service.login(form_data, user_agent)
            resp["user_id"] = str(user_id)
        except EntityNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{form_data.username}' not found",
            )
        except AuthorizationException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
        return LoginResponse(**resp)


@router.post("/logout", response_model=str, summary="Logout", description="Revokes access and refresh tokens")
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    try:
        await auth_service.logout(auth_credentials.credentials)
        return "You're logged out"
    except AuthorizationException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)


@router.post(
    "/refresh_token",
    response_model=Token,
    summary="Refresh token",
    description="Returns new access and refresh tokens for user",
)
async def refresh_token(
    auth_service: AuthService = Depends(get_auth_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("refresh_token"):
        try:
            return await auth_service.refresh_token(auth_credentials.credentials)
        except AuthorizationException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)


@router.get(
    "/login_history",
    response_model=list[LoginHistory],
    summary="Get login history",
    description="Returns all login history records for user",
)
async def login_history(
    offset: int | None = 0,
    limit: int | None = 20,
    auth_service: AuthService = Depends(get_auth_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("login_history"):
        try:
            history_records = await auth_service.get_login_history(auth_credentials.credentials)
            pagination_data = history_records[offset : offset + limit]
            return [LoginHistory(**record) for record in pagination_data]
        except AuthorizationException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)


@router.put(
    "/reset_username",
    response_model=str,
    summary="Reset username",
    description="Changes user username to specified, if new username is not already in use",
)
async def reset_username(
    new_username: NewUsername,
    auth_service: AuthService = Depends(get_auth_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("reset_username"):
        try:
            await auth_service.reset_username(new_username.username, auth_credentials.credentials)
            return f"Username was successfully changed to: {new_username}"
        except DuplicateEntityException:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already in use")
        except AuthorizationException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)


@router.put(
    "/reset_password", response_model=str, summary="Reset password", description="Changes user password to specified"
)
async def reset_password(
    new_password: NewPassword,
    auth_service: AuthService = Depends(get_auth_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    with tracer.start_as_current_span("reset_password"):
        try:
            await auth_service.reset_password(new_password.password, auth_credentials.credentials)
            return "Password was successfully changed"
        except AuthorizationException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)


@router.get(
    "/verify_token",
    response_model=AuthUserResponse,
    summary="Verify provided token",
    description="Verify provided token",
)
async def verify_token(
    auth_service: AuthService = Depends(get_auth_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    try:
        auth_user_data = await auth_service.verify_access_token(auth_credentials.credentials)
        return AuthUserResponse(**auth_user_data)
    except (AuthorizationException, EntityNotFoundException):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)


@router.put(
    "/verify_user_credentials",
    response_model=AuthUserResponse,
    summary="Verify provided login and password",
    description="Verify provided login and password",
)
async def verify_user_credentials(
    form_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        auth_user_data = await auth_service.verify_user_credentials(form_data)
        return AuthUserResponse(**auth_user_data)
    except (AuthorizationException, EntityNotFoundException):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)


@router.get(
    "/get_user_friends",
    response_model=list[FriendResponse],
    summary="Get a list of the user's friends",
    description="Get a list of the user's friends",
)
async def get_user_friends(
    auth_service: AuthService = Depends(get_auth_service),
    auth_credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    try:
        friends = await auth_service.get_friends(auth_credentials.credentials)
        users = friends.get("friends", [])
        formatted_users = [
            FriendResponse(
                id=str(user.id), username=user.username, first_name=user.first_name, last_name=user.last_name
            )
            for user in users
        ]

        return formatted_users
    except (AuthorizationException, EntityNotFoundException):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
