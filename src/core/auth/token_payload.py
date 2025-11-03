
from typing import Optional
from pydantic import BaseModel

from .token_type import TokenType
from .register_token_decorator import register_token


class BasePayload(BaseModel):
    user_id: str
    role: Optional[str] = None


@register_token(
    TokenType.ACCESS_TOKEN.value,
    secret_key="special-access-key",
    minutes=60
)
class AccessTokenPayload(BasePayload):
    pass


@register_token(
    TokenType.REFRESH_TOKEN.value,
    secret_key="special-refresh-key",
    minutes=60 * 24 * 30
)
class RefreshTokenPayload(BasePayload):
    pass


@register_token(
    TokenType.EMAIL_VERIFICATION_TOKEN.value,
    secret_key="special-email-key",
    minutes=30
)
class EmailVerificationPayload(BasePayload):
    email: Optional[str] = None


@register_token(
    TokenType.PASSWORD_RESET_TOKEN.value,
    secret_key="special-password-reset-key",
    minutes=15
)
class PasswordResetPayload(BasePayload):
    email: Optional[str] = None
