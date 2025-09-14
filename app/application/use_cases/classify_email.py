from typing import Optional
from datetime import datetime
from app.domain.entities import Email, ClassificationResult, ClassificationLog
from app.domain.ports import (
    TokenizerPort, ClassifierPort, ReplySuggesterPort, ProfilePort, LogRepositoryPort,
)
from app.domain.errors import BadRequest


 

class FileFacade:

    def __init__(self, pdf_extractor, txt_extractor, eml_extractor):
        self._pdf = pdf_extractor
        self._txt = txt_extractor
        self._eml = eml_extractor

    def from_upload(self, filename: str, raw: bytes) -> str:
        name = (filename or "").lower()
        if name.endswith(".pdf"):
            return self._pdf.extract(raw)
        if name.endswith(".txt"):
            return self._txt.extract(raw)
        if name.endswith(".eml"):
            if not self._eml:
                raise BadRequest("EML extractor não configurado.")
            return self._eml.extract(raw)
        raise BadRequest("Supported files: .pdf or .txt")
    

from datetime import datetime
from typing import Optional
from app.domain.entities import Email, ClassificationResult
from app.domain.errors import BadRequest
from app.domain.ports import TokenizerPort, ClassifierPort, ReplySuggesterPort, ProfilePort, LogRepositoryPort
from app.domain.entities import ClassificationLog


class FileFacade:
    """Converte upload (.pdf/.txt/.eml) para texto bruto."""
    def __init__(self, pdf_extractor, txt_extractor, eml_extractor=None):
        self._pdf = pdf_extractor
        self._txt = txt_extractor
        self._eml = eml_extractor

    def from_upload(self, filename: str, raw: bytes) -> str:
        name = (filename or "").lower()
        if name.endswith(".pdf"):
            return self._pdf.extract(raw)
        if name.endswith(".txt"):
            return self._txt.extract(raw)
        if name.endswith(".eml"):
            if not self._eml:
                raise BadRequest("EML extractor não configurado.")
            return self._eml.extract(raw)
        raise BadRequest("Supported files: .pdf, .txt ou .eml")


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

    # >>> FALTAVA ESTE MÉTODO <<<
    def _expand_priority(self, profile: dict) -> list[str]:
        """
        Expande keywords + sinônimos do profile para melhorar o sinal:
        - normaliza tudo para lowercase
        - combina priority_keywords e keyword_synonyms (se existirem)
        """
        base = (profile.get("priority_keywords") or [])
        syns = (profile.get("keyword_synonyms") or {})
        expanded = set(map(str.lower, base))
        for k, arr in syns.items():
            expanded.add(str(k).lower())
            for s in arr:
                expanded.add(str(s).lower())
        return list(expanded)

    def _classify_and_log(
        self,
        email: Email,
        profile_id: str,
        source: str,
        file_name: Optional[str] = None,
    ) -> ClassificationResult:
        profile = self.profiles.get_profile(profile_id)
        if not profile:
            raise BadRequest(f"Perfil '{profile_id}' não encontrado")

        pre = self.tokenizer.preprocess(email.body)
        tokens = self.tokenizer.tokenize(pre)

        # usa o profile expandido (keywords + sinônimos)
        result = self.classifier.classify(
            email,
            tokens,
            mood=profile.get("mood"),
            priority=self._expand_priority(profile),
        )

        reply = self.responder.suggest(result, email)
        final_result = type(result)(**{**result.__dict__, "suggested_reply": reply})

        log = ClassificationLog(
            id=None,
            created_at=datetime.utcnow(),
            source=source,
            subject=email.subject,
            body_excerpt=(email.body or "")[:500],
            sender=email.sender,
            file_name=file_name,
            profile_id=profile_id,
            category=final_result.category.value,
            reason=final_result.reason,
            suggested_reply=final_result.suggested_reply,
            used_model=final_result.used_model,
            provider="openai",  # pode parametrizar
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
        email = Email(subject=subject, body=body, sender=sender)
        return self._classify_and_log(email, profile_id, source, file_name)

    def execute_from_file(
        self,
        filename: str,
        raw: bytes,
        profile_id: Optional[str] = None,
        subject: Optional[str] = None,
        sender: Optional[str] = None,
    ) -> ClassificationResult:
        if not profile_id:
            profile_id = "default"
        text = self.file_facade.from_upload(filename, raw)
        email = Email(subject=subject, body=text, sender=sender)
        return self._classify_and_log(email, profile_id, source="file", file_name=filename)
