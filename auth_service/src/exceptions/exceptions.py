from fastapi import HTTPException, status

INVALID_CREDENTIALS = "Could not validate credentials"


class EntityNotFoundException(Exception):
    pass


class DuplicateEntityException(Exception):
    pass


class AuthorizationException(Exception):
    pass
