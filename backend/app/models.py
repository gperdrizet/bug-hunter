import enum
import uuid
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Topic(str, enum.Enum):
    DATA_TYPES = "data_types"
    DATA_STRUCTURES = "data_structures"
    OPERATORS = "operators"
    LOOPS = "loops"
    FUNCTIONS = "functions"
    CLASSES = "classes"
    ERROR_HANDLING = "error_handling"
    COMPREHENSIONS = "comprehensions"
    DECORATORS = "decorators"
    GENERATORS = "generators"
    FILE_IO = "file_io"
    EXCEPTIONS = "exceptions"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    used_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    invite_code_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("invite_codes.id", ondelete="SET NULL"), nullable=True
    )

    snippet_records: Mapped[list["UserSnippetRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Snippet(Base):
    __tablename__ = "snippets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic: Mapped[Topic] = mapped_column(Enum(Topic), nullable=False, index=True)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    working_code: Mapped[str] = mapped_column(Text, nullable=False)
    broken_code: Mapped[str] = mapped_column(Text, nullable=False)
    test_cases: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    llm_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_records: Mapped[list["UserSnippetRecord"]] = relationship(
        back_populates="snippet", cascade="all, delete-orphan"
    )


class UserSnippetRecord(Base):
    __tablename__ = "user_snippet_records"
    __table_args__ = (UniqueConstraint("user_id", "snippet_id", name="uq_user_snippet"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snippet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("snippets.id", ondelete="CASCADE"), nullable=False
    )
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    solved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    solved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    in_progress_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="snippet_records")
    snippet: Mapped["Snippet"] = relationship(back_populates="user_records")
