import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.database import get_async_session
from app.models import Difficulty, InviteCode, Snippet, Topic, User, UserSnippetRecord
from app.pipeline import generate_snippet

router = APIRouter(prefix="/admin", tags=["admin"])

# In-memory job store (sufficient for single-instance deployment)
_jobs: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Invite codes
# ---------------------------------------------------------------------------

class InviteCodeOut(BaseModel):
    id: int
    code: str
    is_active: bool
    created_at: datetime
    used_at: datetime | None
    used_by_id: str | None


class GenerateCodesRequest(BaseModel):
    count: int = 1


@router.get("/invite-codes", response_model=list[InviteCodeOut])
async def list_invite_codes(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(InviteCode).order_by(InviteCode.created_at.desc()))
    codes = result.scalars().all()
    return [
        InviteCodeOut(
            id=c.id,
            code=c.code,
            is_active=c.is_active,
            created_at=c.created_at,
            used_at=c.used_at,
            used_by_id=str(c.used_by_id) if c.used_by_id else None,
        )
        for c in codes
    ]


@router.post("/invite-codes/generate", response_model=list[InviteCodeOut])
async def generate_invite_codes(
    body: GenerateCodesRequest,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    if body.count < 1 or body.count > 100:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 100.")
    codes = []
    for _ in range(body.count):
        invite = InviteCode(
            code=secrets.token_urlsafe(16),
            created_by_id=admin.id,
            is_active=True,
        )
        session.add(invite)
        codes.append(invite)
    await session.flush()
    await session.commit()
    for c in codes:
        await session.refresh(c)
    return [
        InviteCodeOut(
            id=c.id,
            code=c.code,
            is_active=c.is_active,
            created_at=c.created_at,
            used_at=c.used_at,
            used_by_id=str(c.used_by_id) if c.used_by_id else None,
        )
        for c in codes
    ]


@router.delete("/invite-codes/{code_id}")
async def revoke_invite_code(
    code_id: int,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(InviteCode).where(InviteCode.id == code_id))
    invite = result.scalar_one_or_none()
    if invite is None:
        raise HTTPException(status_code=404, detail="Invite code not found.")
    invite.is_active = False
    session.add(invite)
    await session.commit()
    return {"revoked": True}


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

class UserAdminOut(BaseModel):
    id: str
    email: str
    display_name: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime


@router.get("/users", response_model=list[UserAdminOut])
async def list_users(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        UserAdminOut(
            id=str(u.id),
            email=u.email,
            display_name=u.display_name,
            is_active=u.is_active,
            is_admin=u.is_admin,
            created_at=u.created_at,
        )
        for u in users
    ]


class UpdateUserRequest(BaseModel):
    is_active: bool | None = None
    is_admin: bool | None = None
    display_name: str | None = None


@router.patch("/users/{user_id}", response_model=UserAdminOut)
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    uid = uuid.UUID(user_id)
    result = await session.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.is_admin is not None:
        user.is_admin = body.is_admin
    if body.display_name is not None:
        user.display_name = body.display_name
    session.add(user)
    await session.commit()
    return UserAdminOut(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    uid = uuid.UUID(user_id)
    result = await session.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    await session.delete(user)
    await session.commit()
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Snippet management
# ---------------------------------------------------------------------------

class SnippetAdminOut(BaseModel):
    id: str
    topic: str
    difficulty: str
    title: str
    working_code: str
    broken_code: str
    test_cases: list[dict]
    llm_provider: str
    llm_model: str
    is_active: bool
    created_at: datetime


class UpdateSnippetRequest(BaseModel):
    title: str | None = None
    working_code: str | None = None
    broken_code: str | None = None
    test_cases: list[dict] | None = None
    is_active: bool | None = None


class CreateSnippetRequest(BaseModel):
    topic: Topic
    difficulty: Difficulty
    title: str
    working_code: str
    broken_code: str
    test_cases: list[dict]


@router.get("/snippets", response_model=list[SnippetAdminOut])
async def list_snippets(
    topic: Topic | None = None,
    difficulty: Difficulty | None = None,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Snippet).order_by(Snippet.created_at.desc())
    if topic:
        query = query.where(Snippet.topic == topic)
    if difficulty:
        query = query.where(Snippet.difficulty == difficulty)
    result = await session.execute(query)
    snippets = result.scalars().all()
    return [_snippet_out(s) for s in snippets]


@router.post("/snippets", response_model=SnippetAdminOut, status_code=201)
async def create_snippet_manual(
    body: CreateSnippetRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    snippet = Snippet(
        topic=body.topic,
        difficulty=body.difficulty,
        title=body.title,
        working_code=body.working_code,
        broken_code=body.broken_code,
        test_cases=body.test_cases,
        llm_provider="manual",
        llm_model="manual",
    )
    session.add(snippet)
    await session.commit()
    await session.refresh(snippet)
    return _snippet_out(snippet)


@router.patch("/snippets/{snippet_id}", response_model=SnippetAdminOut)
async def update_snippet(
    snippet_id: str,
    body: UpdateSnippetRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    sid = uuid.UUID(snippet_id)
    result = await session.execute(select(Snippet).where(Snippet.id == sid))
    snippet = result.scalar_one_or_none()
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found.")
    for field in ("title", "working_code", "broken_code", "test_cases", "is_active"):
        val = getattr(body, field)
        if val is not None:
            setattr(snippet, field, val)
    session.add(snippet)
    await session.commit()
    return _snippet_out(snippet)


@router.delete("/snippets/{snippet_id}")
async def delete_snippet(
    snippet_id: str,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    sid = uuid.UUID(snippet_id)
    result = await session.execute(select(Snippet).where(Snippet.id == sid))
    snippet = result.scalar_one_or_none()
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found.")
    await session.delete(snippet)
    await session.commit()
    return {"deleted": True}


# ---------------------------------------------------------------------------
# LLM generation jobs
# ---------------------------------------------------------------------------

class GenerateSnippetRequest(BaseModel):
    topic: Topic
    difficulty: Difficulty


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending | running | done | failed
    snippet_id: str | None = None
    error: str | None = None


@router.post("/snippets/generate", response_model=JobStatus, status_code=202)
async def trigger_generation(
    body: GenerateSnippetRequest,
    background_tasks: BackgroundTasks,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_async_session),
):
    job_id = secrets.token_hex(8)
    _jobs[job_id] = {"status": "pending", "snippet_id": None, "error": None}
    background_tasks.add_task(_run_generation_job, job_id, body.topic, body.difficulty)
    return JobStatus(job_id=job_id, status="pending")


@router.get("/snippets/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str, admin=Depends(require_admin)):
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JobStatus(job_id=job_id, **job)


async def _run_generation_job(job_id: str, topic: Topic, difficulty: Difficulty):
    from app.database import async_session_maker

    _jobs[job_id]["status"] = "running"
    try:
        data = await generate_snippet(topic, difficulty)
        async with async_session_maker() as session:
            snippet = Snippet(**data)
            session.add(snippet)
            await session.commit()
            await session.refresh(snippet)
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["snippet_id"] = str(snippet.id)
    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(exc)


def _snippet_out(s: Snippet) -> SnippetAdminOut:
    return SnippetAdminOut(
        id=str(s.id),
        topic=s.topic.value,
        difficulty=s.difficulty.value,
        title=s.title,
        working_code=s.working_code,
        broken_code=s.broken_code,
        test_cases=s.test_cases,
        llm_provider=s.llm_provider,
        llm_model=s.llm_model,
        is_active=s.is_active,
        created_at=s.created_at,
    )
