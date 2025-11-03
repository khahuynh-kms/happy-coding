from functools import wraps
from typing import Annotated, List, Optional
from beanie import PydanticObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from ..users.models import User
from ..users.schemas import UserResponse
from ..users.service import user_service

from ...core.auth.security_service import SecurityService
from ...core.auth.token_payload import AccessTokenPayload


_reusable_oauth2 = HTTPBearer(scheme_name='Authorization')
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_token(
    bearer_token: str = Depends(_reusable_oauth2),
    oauth_token: str = Depends(_oauth2_scheme),
) -> str:
    """
    Extract token from either OAuth2PasswordBearer or HTTPBearer.
    Preference: OAuth2 first, then HTTPBearer.
    """
    if oauth_token:
        return oauth_token
    if bearer_token and bearer_token.credentials:
        return bearer_token.credentials

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


async def get_current_user(token: str = Depends(get_token)) -> dict:
    payload = SecurityService.decode_token(token, AccessTokenPayload)
    user_id = payload["user_id"]
    role = payload.get("role")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"id": user_id, "role": role}


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    exist_user = await user_service.find_one(current_user["id"])
    user = UserResponse.model_validate(exist_user)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


def require_roles(*allowed_roles, exclude: Optional[List[str]] = []):
    if not allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Needed to provide roles for route"
        )

    allowed_roles = [role for role in allowed_roles]

    """
    Decorator to restrict access to one or more roles.
    Usage: @require_roles("admin", "user")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(
            current_user: UserResponse = Depends(get_current_active_user),
            *args,
            **kwargs,
        ):
            current_user = current_user.model_dump()
            role = current_user["role"] or None
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="The user hasn't configured the role"
                )

            if role not in allowed_roles or role in exclude:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden to access"
                )

            return func(*args, **kwargs, current_user=current_user)
        return wrapper
    return decorator
