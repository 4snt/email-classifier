from pydantic import BaseModel
import os

class Settings(BaseModel):
    USE_OPENAI: bool = bool(os.getenv("OPENAI_API_KEY"))

settings = Settings()
