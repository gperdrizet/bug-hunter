import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.database import get_async_session
from app.models import Snippet, User, UserSnippetRecord

router = APIRouter(prefix="/attempts", tags=["attempts"])


class TestResult(BaseModel):
    name: str
    passed: bool
    stdout: str
    error: str | None = None


class SubmitAttemptRequest(BaseModel):
    snippet_id: str
    tests: list[TestResult]


class SaveCodeRequest(BaseModel):
    code: str


async def _get_record(
    session: AsyncSession, user_id: uuid.UUID, snippet_id: uuid.UUID
) -> UserSnippetRecord:
    result = await session.execute(
        select(UserSnippetRecord).where(
            UserSnippetRecord.user_id == user_id,
            UserSnippetRecord.snippet_id == snippet_id,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snippet not started.")
    return record


@router.post("/submit")
async def submit_attempt(
    body: SubmitAttemptRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    snippet_id = uuid.UUID(body.snippet_id)
    record = await _get_record(session, user.id, snippet_id)

    all_passed = all(t.passed for t in body.tests)
    now = datetime.now(timezone.utc)

    record.attempt_count += 1
    record.last_attempt_at = now

    if all_passed and not record.solved:
        record.solved = True
        record.solved_at = now
        record.in_progress_code = None  # Clear draft on solve

    session.add(record)
    await session.commit()

    return {"solved": record.solved, "attempt_count": record.attempt_count}


@router.patch("/{snippet_id}/code")
async def save_in_progress_code(
    snippet_id: str,
    body: SaveCodeRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    sid = uuid.UUID(snippet_id)
    record = await _get_record(session, user.id, sid)

    if record.solved:
        # Don't overwrite cleared code on a solved snippet
        return {"saved": False}

    record.in_progress_code = body.code
    session.add(record)
    await session.commit()
    return {"saved": True}
