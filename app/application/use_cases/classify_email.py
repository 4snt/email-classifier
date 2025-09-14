from typing import Optional
from datetime import datetime
from app.domain.entities import Email, ClassificationResult, ClassificationLog
from app.domain.ports import (
    TokenizerPort,
    ClassifierPort,
    ReplySuggesterPort,
    ProfilePort,
    LogRepositoryPort,
)
from app.domain.errors import BadRequest


class FileFacade:
    """Converte upload (.pdf/.txt) para texto bruto."""

    def __init__(self, pdf_extractor, txt_extractor):
        self._pdf = pdf_extractor
        self._txt = txt_extractor

    def from_upload(self, filename: str, raw: bytes) -> str:
        name = (filename or "").lower()
        if name.endswith(".pdf"):
            return self._pdf.extract(raw)
        if name.endswith(".txt"):
            return self._txt.extract(raw)
        raise BadRequest("Supported files: .pdf or .txt")


class ClassifyEmailUseCase:
    def __init__(
        self,
        file_facade: FileFacade,
        tokenizer: TokenizerPort,
        classifier: ClassifierPort,
        responder: ReplySuggesterPort,
        profiles: ProfilePort,
        log_repo: LogRepositoryPort, 
    ):
        self.file_facade = file_facade
        self.tokenizer = tokenizer
        self.classifier = classifier
        self.responder = responder
        self.profiles = profiles
        self.log_repo = log_repo

    def execute_from_text(
        self,
        subject: str,
        body: str,
        sender: Optional[str] = None,
        profile_id: Optional[str] = None,
        source: str = "json",
        file_name: Optional[str] = None,
    ) -> ClassificationResult:
        if not profile_id:
            profile_id = "default"

        profile = self.profiles.get_profile(profile_id)
        if not profile:
            raise BadRequest(f"Perfil '{profile_id}' não encontrado")

        email = Email(subject=subject, body=body, sender=sender)
        pre = self.tokenizer.preprocess(email.body)
        tokens = self.tokenizer.tokenize(pre)

        result = self.classifier.classify(
            email,
            tokens,
            mood=profile.get("mood"),
            priority=profile.get("priority_keywords"),
        )

        reply = self.responder.suggest(result, email)
        final_result = type(result)(**{**result.__dict__, "suggested_reply": reply})

        log = ClassificationLog(
            id=None,
            created_at=datetime.utcnow(),
            source=source,
            subject=subject,
            body_excerpt=body[:500],
            sender=sender,
            file_name=file_name,
            profile_id=profile_id,
            category=final_result.category.value,
            reason=final_result.reason,
            suggested_reply=final_result.suggested_reply,
            used_model=final_result.used_model,
            provider="openai",  
            prompt_tokens=final_result.prompt_tokens,
            completion_tokens=final_result.completion_tokens,
            total_tokens=final_result.total_tokens,
            cost_usd=0.0,
            latency_ms=None,
            status="ok",
            error=None,
            extra=final_result.extra,
        )
        self.log_repo.save(log)

        return final_result

    def execute_from_file(
        self,
        filename: str,
        raw: bytes,
        profile_id: Optional[str] = None,
        subject: Optional[str] = None,
        sender: Optional[str] = None,
    ) -> ClassificationResult:
        text = self.file_facade.from_upload(filename, raw)
        return self.execute_from_text(
            subject=subject,
            body=text,
            sender=sender,
            profile_id=profile_id,
            source="file",
            file_name=filename,
        )
