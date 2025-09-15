from dataclasses import dataclass
from enum import Enum
from datetime import datetime 
from typing import Optional, Dict , Any

class Category(str, Enum):
    PRODUCTIVE = "productive"
    UNPRODUCTIVE = "unproductive"

@dataclass
class Email:
    subject: Optional[str]
    body: str
    sender: Optional[str] = None
    
@dataclass
class ClassificationResult:
    category: Category
    reason: str
    suggested_reply: str
    used_model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    extra: Optional[Dict[str, Any]] = None   
    
@dataclass
class ClassificationLog:
    id: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    source: str = "imap"
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
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    latency_ms: Optional[int] = None

    status: str = "success"
    error: Optional[str] = None

    extra: Optional[Dict[str, Any]] = None
    
@dataclass
class User:
    id: Optional[int]
    username: str
    password_hash: str