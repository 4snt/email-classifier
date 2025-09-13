from pydantic import BaseModel, Field
from typing import Optional
from app.domain.entities import Category

class DirectJson(BaseModel):
    subject: Optional[str] = None
    body: str = Field(min_length=1)
    sender: Optional[str] = None

class ClassifyResponse(BaseModel):
    category: Category
    confidence: float
    reason: str
    suggested_reply: str
