import smtplib
import uuid
from email.mime.text import MIMEText

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_async_session
from app.models import User


def _send_email(to: str, subject: str, body: str) -> None:
    """Send a plain-text email via SMTP, or log to console when SMTP is not configured."""
    if not settings.smtp_host:
        print(f"[DEV] Email to {to}\nSubject: {subject}\n{body}")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request: Request | None = None):
        pass  # invite code consumption happens in the custom register route

    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None):
        reset_url = f"{settings.app_url}/reset-password?token={token}"
        _send_email(
            to=user.email,
            subject="Reset your Bug Hunter password",
            body=(
                f"Hi,\n\n"
                f"Click the link below to reset your password. "
                f"This link expires in 1 hour.\n\n"
                f"{reset_url}\n\n"
                f"If you didn't request a password reset, you can ignore this email."
            ),
        )

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None):
        verify_url = f"{settings.app_url}/verify-email?token={token}"
        _send_email(
            to=user.email,
            subject="Verify your Bug Hunter email address",
            body=(
                f"Hi,\n\n"
                f"Click the link below to verify your email address.\n\n"
                f"{verify_url}\n\n"
                f"If you didn't create a Bug Hunter account, you can ignore this email."
            ),
        )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=60 * 60 * 24 * 7)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_admin_user = fastapi_users.current_user(active=True, superuser=False)


async def require_admin(user: User = Depends(current_active_user)) -> User:
    if not user.is_admin:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
