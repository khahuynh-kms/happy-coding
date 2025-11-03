import logging
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated
from .dependencies import get_current_active_user, require_roles
from .schemas import (
    AuthResponse, LoginWithCredential,
    RegisterResponse, RegisterWithCredential,
    ResetPassword, ResetPasswordRequest, UserChangePasswordRequest
)
from ..users.schemas import UserChangePassword, UserResponse, UserUpdate
from ..users.models import User
from ..users.service import user_service
from ...core.libs.mailing.payloads.auth_pr import (
    ResetPasswordPayload, WelcomePayload
)
from ...core.libs.mailing.mail_service import MailService, mail_service
from ...core.libs.paypal.paypal_service import list_payments
from ...core.auth.token_type import TokenType
from ...core.auth.token_payload import (
    AccessTokenPayload,
    EmailVerificationPayload,
    PasswordResetPayload,
    RefreshTokenPayload
)
from ...core.auth.security_service import SecurityService


router = APIRouter(prefix="/auth", tags=["Auth"])
base_url = "http://localhost:8000"


@router.get("/t")
async def name():
    return await list_payments(10)


@router.post("/login", response_model=AuthResponse)
async def login(auth: LoginWithCredential):
    if not auth.email:
        raise HTTPException(
            status_code=400, detail="Your provided credentials is wrong"
        )

    user = await user_service.find_by_email(email=auth.email)

    if (
        not user or not SecurityService.verify_password(
            auth.password, user.password)
    ):
        raise HTTPException(
            status_code=400, detail="Your provided credentials is wrong"
        )

    try:
        access_token = SecurityService.create_token(
            AccessTokenPayload(user_id=str(user.id), role=user.role)
        )
        refresh_token = SecurityService.create_token(
            RefreshTokenPayload(user_id=str(user.id))
        )

    except Exception as e:
        logging.error(f"Unexpected error in create token: {e}")
        raise HTTPException(status_code=500, detail="Failed to create tokens")

    return {
        "access_token": access_token[AccessTokenPayload.__token_type__],
        "exp": access_token["exp"],
        "refresh_token": refresh_token[RefreshTokenPayload.__token_type__],
    }


@router.get("/me", dependencies=[Depends(get_current_active_user)])
def read_user_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/admin", dependencies=[Depends(get_current_active_user)],
            response_model=UserResponse)
@require_roles("admin")
def allow_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/user", dependencies=[Depends(get_current_active_user)],
            response_model=UserResponse)
@require_roles("user")
def allow_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/admin-user",
            dependencies=[Depends(get_current_active_user)],
            response_model=UserResponse)
@require_roles("admin", "user")
def allow_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.post("/register", response_model=RegisterResponse)
async def register(
    auth: RegisterWithCredential,
    email_service: MailService = Depends(mail_service)
):
    if not auth.email and not (auth.password):
        raise HTTPException(
            status_code=400, detail="Your credential is required"
        )
    payload = auth.model_copy(
        update={"password": SecurityService.hash_password(auth.password)},
    ).model_dump()
    created_user = await user_service.create({**payload, "role": "user"})

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    if created_user:
        logging.info(f"User {created_user.email} created successfully")
        logging.info("Sending email verification link...")

        email_token = SecurityService.create_token(EmailVerificationPayload(
            user_id=str(created_user.id), email=created_user.email
        ))
        email_verification_link = (
            f"{base_url}/auth/email-verification?"
            f"token={email_token[TokenType.EMAIL_VERIFICATION_TOKEN.value]}"
            f"&type={TokenType.EMAIL_VERIFICATION_TOKEN.value}"
        )
        email_service.send_mail(created_user.email, WelcomePayload(
            full_name=created_user.full_name or created_user.email,
            email_verification_link=email_verification_link,
            username=created_user.email
        ))

        return {
            "message": "User registered successfully", "user": created_user
        }


@router.get("/email-verification", response_model=UserResponse)
async def verify_email(
    token: str = Query("token"), type=Query("type"),
):
    payload = SecurityService.decode_token(token, token_type=type)
    if payload.get("type") != TokenType.EMAIL_VERIFICATION_TOKEN.value:
        raise HTTPException(
            status_code=400, detail="Invalid provided token"
        )

    user_id = payload.get("user_id")
    email = payload.get("email")
    if not (user_id and email):
        raise HTTPException(
            status_code=400, detail="Invalid provided token"
        )

    return await user_service.update(
        PydanticObjectId(user_id),
        UserUpdate(email_verified=True)
    )


@router.post("/request-reset-password")
async def request_reset_password(
    request: ResetPasswordRequest,
    email_service: MailService = Depends(mail_service)
):
    user = await user_service.get_by_email(email=request.email)
    if not user:
        raise HTTPException(
            status_code=404, detail="User is not found"
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=400,
            detail="Email had not been provided or verified yet"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Your account is inactive. Please contact admin."
        )

    logging.info(f"Sending password reset link to {user.email}...")
    reset_token = SecurityService.create_token(PasswordResetPayload(
        user_id=str(user.id), email=user.email
    ))
    password_reset_link = (
        f"{base_url}/auth/password-reset?"
        f"token={reset_token[TokenType.PASSWORD_RESET_TOKEN.value]}"
        f"&type={TokenType.PASSWORD_RESET_TOKEN.value}"
    )

    email_service.send_mail(
        subject="Password Reset",
        to_email=user.email,
        model=ResetPasswordPayload(
            full_name=user.full_name or user.email,
            password_reset_link=password_reset_link,
        )
    )

    return {"message": "Password reset link has been sent to your email"}


@router.post("/password-reset", response_model=UserResponse)
async def password_reset(request: ResetPassword):
    payload = SecurityService.decode_token(
        request.token,
        PasswordResetPayload
    )
    user_id = payload.get("user_id")
    email = payload.get("email")
    if not (user_id and email):
        raise HTTPException(status_code=400, detail="Invalid provided token")

    return await user_service.update(
        PydanticObjectId(user_id),
        UserChangePassword(
            password=SecurityService.hash_password(request.password)
        )
    )


@router.post(
    "/change-password", response_model=UserResponse,
    dependencies=[Depends(get_current_active_user)]
)
async def change_password(
    request: UserChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    current_user = await user_service.find_one(current_user.id)
    if not current_user:
        raise HTTPException(status_code=404, detail="User is not found")

    if (
        not SecurityService.verify_password(
            request.current_password, current_user.password)
    ):
        raise HTTPException(
            status_code=400, detail="Your current password is incorrect"
        )

    return await user_service.update(
        current_user.id,
        UserChangePassword(
            password=SecurityService.hash_password(request.new_password)
        )
    )
