from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict , Any

class Category(str, Enum):
    PRODUCTIVE = "productive"
    UNPRODUCTIVE = "unproductive"

@dataclass(frozen=True)
class Email:
    subject: Optional[str]
    body: str
    sender: Optional[str] = None

@dataclass(frozen=True)
class ClassificationResult:
    category: Category
    reason: str
    suggested_reply: str
    used_model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    extra: Optional[Dict[str, Any]] = None   