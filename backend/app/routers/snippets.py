import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.database import get_async_session
from app.models import Difficulty, Snippet, Topic, User, UserSnippetRecord

router = APIRouter(prefix="/snippets", tags=["snippets"])


class SnippetResponse(BaseModel):
    id: str
    topic: str
    difficulty: str
    title: str
    broken_code: str
    test_cases: list[dict]
    in_progress_code: str | None


async def _get_or_create_record(
    session: AsyncSession, user_id: uuid.UUID, snippet: Snippet
) -> UserSnippetRecord:
    result = await session.execute(
        select(UserSnippetRecord).where(
            UserSnippetRecord.user_id == user_id,
            UserSnippetRecord.snippet_id == snippet.id,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = UserSnippetRecord(user_id=user_id, snippet_id=snippet.id)
        session.add(record)
        await session.flush()
    return record


@router.get("/next", response_model=SnippetResponse)
async def get_next_snippet(
    topic: Topic,
    difficulty: Difficulty,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Find snippets this user has already seen for this topic+difficulty
    seen_subq = (
        select(UserSnippetRecord.snippet_id)
        .where(UserSnippetRecord.user_id == user.id)
        .scalar_subquery()
    )

    result = await session.execute(
        select(Snippet)
        .where(
            Snippet.topic == topic,
            Snippet.difficulty == difficulty,
            Snippet.is_active == True,
            Snippet.id.not_in(seen_subq),
        )
        .order_by(func.random())
        .limit(1)
    )
    snippet = result.scalar_one_or_none()

    if snippet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unseen snippets available for this topic and difficulty. Try generating more in the admin panel.",
        )

    record = await _get_or_create_record(session, user.id, snippet)
    await session.commit()

    return SnippetResponse(
        id=str(snippet.id),
        topic=snippet.topic.value,
        difficulty=snippet.difficulty.value,
        title=snippet.title,
        broken_code=snippet.broken_code,
        test_cases=snippet.test_cases,
        in_progress_code=record.in_progress_code,
    )


@router.get("/{snippet_id}", response_model=SnippetResponse)
async def get_snippet_by_id(
    snippet_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        sid = uuid.UUID(snippet_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid snippet ID.")

    result = await session.execute(
        select(Snippet).where(Snippet.id == sid, Snippet.is_active == True)
    )
    snippet = result.scalar_one_or_none()
    if snippet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snippet not found.")

    record = await _get_or_create_record(session, user.id, snippet)
    await session.commit()

    return SnippetResponse(
        id=str(snippet.id),
        topic=snippet.topic.value,
        difficulty=snippet.difficulty.value,
        title=snippet.title,
        broken_code=snippet.broken_code,
        test_cases=snippet.test_cases,
        in_progress_code=record.in_progress_code,
    )
