from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.database import get_async_session
from app.models import Snippet, User, UserSnippetRecord

router = APIRouter(prefix="/me", tags=["users"])


class TopicStats(BaseModel):
    topic: str
    solved: int
    attempted: int


class UserStats(BaseModel):
    total_solved: int
    total_attempted: int
    success_rate: float
    by_topic: list[TopicStats]


class SnippetSummary(BaseModel):
    snippet_id: str
    title: str
    topic: str
    difficulty: str
    solved_at: datetime | None
    attempt_count: int


@router.get("/stats", response_model=UserStats)
async def get_my_stats(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(UserSnippetRecord, Snippet)
        .join(Snippet, UserSnippetRecord.snippet_id == Snippet.id)
        .where(UserSnippetRecord.user_id == user.id, UserSnippetRecord.attempt_count > 0)
    )
    rows = result.all()

    total_attempted = len(rows)
    total_solved = sum(1 for r, _ in rows if r.solved)
    success_rate = (total_solved / total_attempted * 100) if total_attempted else 0.0

    by_topic: dict[str, dict] = {}
    for record, snippet in rows:
        t = snippet.topic.value
        if t not in by_topic:
            by_topic[t] = {"topic": t, "solved": 0, "attempted": 0}
        by_topic[t]["attempted"] += 1
        if record.solved:
            by_topic[t]["solved"] += 1

    return UserStats(
        total_solved=total_solved,
        total_attempted=total_attempted,
        success_rate=round(success_rate, 1),
        by_topic=[TopicStats(**v) for v in by_topic.values()],
    )


@router.get("/history", response_model=list[SnippetSummary])
async def get_my_history(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    solved_only: bool = False,
):
    query = (
        select(UserSnippetRecord, Snippet)
        .join(Snippet, UserSnippetRecord.snippet_id == Snippet.id)
        .where(UserSnippetRecord.user_id == user.id, UserSnippetRecord.attempt_count > 0)
        .order_by(UserSnippetRecord.last_attempt_at.desc().nullslast())
    )
    if solved_only:
        query = query.where(UserSnippetRecord.solved)

    result = await session.execute(query)
    rows = result.all()

    return [
        SnippetSummary(
            snippet_id=str(r.snippet_id),
            title=s.title,
            topic=s.topic.value,
            difficulty=s.difficulty.value,
            solved_at=r.solved_at,
            attempt_count=r.attempt_count,
        )
        for r, s in rows
    ]
