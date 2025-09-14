from typing import Protocol, List, Optional, Dict
from .entities import Email, ClassificationResult

class TextExtractorPort(Protocol):
    def extract(self, raw_bytes: bytes) -> str: ...

class TokenizerPort(Protocol):
    def preprocess(self, text: str) -> str: ...
    def tokenize(self, text: str) -> List[str]: ...

class ClassifierPort(Protocol):
    def classify(
        self,
        email: Email,
        tokens: List[str],
        mood: Optional[str] = None,
        priority: Optional[list[str]] = None
    ) -> ClassificationResult: ...

class ReplySuggesterPort(Protocol):
    def suggest(self, result: ClassificationResult, email: Email) -> str: ...

class ProfilePort(Protocol):
    def get_profile(self, profile_id: str) -> Optional[Dict]:
        ...