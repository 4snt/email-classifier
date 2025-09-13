from dataclasses import dataclass
from enum import Enum
from typing import Optional

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
    confidence: float
    reason: str
    suggested_reply: Optional[str] = None
    total_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
