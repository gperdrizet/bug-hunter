from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import auth_backend, fastapi_users, get_user_manager
from app.database import get_async_session
from app.models import InviteCode, User

router = APIRouter(tags=["auth"])

# Standard fastapi-users login/logout routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None
    invite_code: str


class UserRead(schemas.BaseUser[str]):
    display_name: str | None
    is_admin: bool


@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    request_data: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user_manager=Depends(get_user_manager),
):
    # Validate and claim invite code atomically
    result = await session.execute(
        select(InviteCode).where(
            InviteCode.code == request_data.invite_code,
            InviteCode.is_active,
            InviteCode.used_by_id.is_(None),
        )
    )
    invite = result.scalar_one_or_none()
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid or already-used invite code.",
        )

    # Check email not already registered
    existing = await session.execute(select(User).where(User.email == request_data.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Create user via fastapi-users manager
    from fastapi_users import schemas as fu_schemas

    class _CreateSchema(fu_schemas.BaseUserCreate):
        pass

    user_create = _CreateSchema(email=request_data.email, password=request_data.password)
    user = await user_manager.create(user_create, safe=True, request=request)

    # Set display_name and link invite code
    user.display_name = request_data.display_name
    user.invite_code_id = invite.id
    invite.used_by_id = user.id
    invite.used_at = datetime.now(timezone.utc)
    invite.is_active = False

    session.add(user)
    session.add(invite)
    await session.commit()
    await session.refresh(user)

    return UserRead(
        id=str(user.id),
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
        display_name=user.display_name,
        is_admin=user.is_admin,
    )


@router.get("/auth/me", response_model=UserRead)
async def me(user: User = Depends(fastapi_users.current_user(active=True))):
    return UserRead(
        id=str(user.id),
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
        display_name=user.display_name,
        is_admin=user.is_admin,
    )
