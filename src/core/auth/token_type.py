import enum


class TokenType(enum.Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    EMAIL_VERIFICATION_TOKEN = "email_verification_token"
    PASSWORD_RESET_TOKEN = "password_reset_token"
