from dataclasses import dataclass
from enum import Enum
from datetime import datetime 
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
    
@dataclass(frozen=True)
class ClassificationLog:
    id: Optional[int]
    created_at: datetime
    source: str                  
    subject: Optional[str]
    body_excerpt: Optional[str]
    sender: Optional[str]
    file_name: Optional[str]
    profile_id: Optional[str]

    # Saída
    category: Optional[str]
    reason: Optional[str]
    suggested_reply: Optional[str]

    # Modelo usado
    used_model: Optional[str]
    provider: Optional[str]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    cost_usd: Optional[float]
    latency_ms: Optional[int]

    # Status
    status: str
    error: Optional[str]

    # Extra flexível
    extra: Optional[Dict[str, Any]] = None
    
@dataclass(frozen=True)
class User:
    id: Optional[int]
    username: str
    password_hash: str