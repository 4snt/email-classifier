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
        
from .entities import ClassificationLog

class LogRepositoryPort(Protocol):
    """Porta para persistência de logs de classificação."""

    def save(self, log: ClassificationLog) -> ClassificationLog:
        """Salva um log de classificação no repositório."""
        ...

    def list_recent(self, limit: int = 50) -> List[ClassificationLog]:
        """Retorna os últimos logs de classificação."""
        ...

    def get_by_id(self, log_id: int) -> Optional[ClassificationLog]:
        """Busca um log específico pelo id."""
        ...
class EmailSourcePort(Protocol):
    def fetch_unread(self) -> list[Email]:
        """Busca emails não lidos da fonte (IMAP, Gmail API etc)."""
        ...

    def mark_as_read(self, ids: list[str]) -> None:
        """Marca como lidos (ou move para pasta) depois de processar."""
        ...