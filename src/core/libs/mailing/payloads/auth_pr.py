from dataclasses import dataclass

from ..template_decorator import register_template


@register_template(
    template_name="welcome_email.html",
    default_subject="Welcome and verify your email address"
)
@dataclass
class WelcomePayload:
    full_name: str
    username: str
    email_verification_link: str


@register_template(
    template_name="reset_password.html",
    default_subject="Reset your password"
)
@dataclass
class ResetPasswordPayload:
    full_name: str
    password_reset_link: str
