from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON


class ClassificationLogModel(SQLModel, table=True):
    __tablename__ = "classification_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    source: str = Field(index=True)  
    subject: Optional[str] = None
    body_excerpt: Optional[str] = None
    sender: Optional[str] = None
    file_name: Optional[str] = None
    profile_id: Optional[str] = None

    category: Optional[str] = None
    reason: Optional[str] = None
    suggested_reply: Optional[str] = None

    used_model: Optional[str] = None
    provider: Optional[str] = None
    prompt_tokens: Optional[int] = 0
    completion_tokens: Optional[int] = 0
    total_tokens: Optional[int] = 0
    cost_usd: Optional[float] = None
    latency_ms: Optional[int] = None

    status: str = Field(default="ok")
    error: Optional[str] = None

    extra: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    def to_entity(self):
        from app.domain.entities import ClassificationLog
        return ClassificationLog(
            id=self.id,
            created_at=self.created_at,
            source=self.source,
            subject=self.subject,
            body_excerpt=self.body_excerpt,
            sender=self.sender,
            file_name=self.file_name,
            profile_id=self.profile_id,
            category=self.category,
            reason=self.reason,
            suggested_reply=self.suggested_reply,
            used_model=self.used_model,
            provider=self.provider,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.total_tokens,
            cost_usd=self.cost_usd,
            latency_ms=self.latency_ms,
            status=self.status,
            error=self.error,
            extra=self.extra,
        )

    @classmethod
    def from_entity(cls, log_entity):
        return cls(**log_entity.__dict__)

class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)

    def to_entity(self):
        from app.domain.entities import User
        return User(
            id=self.id,
            username=self.username,
            password_hash=self.password_hash
        )

    @classmethod
    def from_entity(cls, user_entity):
        return cls(**user_entity.__dict__)