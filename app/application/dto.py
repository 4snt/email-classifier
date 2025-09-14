from pydantic import BaseModel, Field
from typing import Optional
from app.domain.entities import Category

class DirectJson(BaseModel):
    subject: Optional[str] = None
    body: str = Field(min_length=1)
    sender: Optional[str] = None
    profile_id:  Optional[str] = None

class ClassifyResponse(BaseModel):
    category: Category
    reason: str
    suggested_reply: str
    used_model: Optional[str] = None 
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"