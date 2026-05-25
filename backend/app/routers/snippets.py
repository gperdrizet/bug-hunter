import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.database import get_async_session
from app.models import Difficulty, Snippet, Topic, User, UserSnippetRecord
from app.pipeline import generate_snippet

router = APIRouter(prefix="/snippets", tags=["snippets"])
logger = logging.getLogger(__name__)


class SnippetResponse(BaseModel):
    id: str
    topic: str
    difficulty: str
    title: str
    description: str | None
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
            Snippet.is_active,
            Snippet.id.not_in(seen_subq),
        )
        .order_by(func.random())
        .limit(1)
    )
    snippet = result.scalar_one_or_none()

    if snippet is None:
        logger.info(
            "No unseen snippet for %s/%s; generating on demand for user %s",
            topic.value, difficulty.value, user.id,
        )
        try:
            neg_result = await session.execute(
                select(Snippet.working_code)
                .where(Snippet.topic == topic, Snippet.difficulty == difficulty, Snippet.is_active)
                .order_by(func.random())
                .limit(5)
            )
            existing_codes = list(neg_result.scalars().all())
            data = await generate_snippet(topic, difficulty, existing_snippets=existing_codes)
            snippet = Snippet(**data)
            session.add(snippet)
            await session.flush()
        except Exception as exc:
            logger.exception("On-demand snippet generation failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not generate a new problem right now. Please try again.",
            )

    record = await _get_or_create_record(session, user.id, snippet)
    await session.commit()

    return SnippetResponse(
        id=str(snippet.id),
        topic=snippet.topic.value,
        difficulty=snippet.difficulty.value,
        title=snippet.title,
        description=snippet.description,
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
        select(Snippet).where(Snippet.id == sid, Snippet.is_active)
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
        description=snippet.description,
        broken_code=snippet.broken_code,
        test_cases=snippet.test_cases,
        in_progress_code=record.in_progress_code,
    )
