from typing import Optional
from app.domain.entities import Email, ClassificationResult
from app.domain.ports import TokenizerPort, ClassifierPort, ReplySuggesterPort, ProfilePort
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
        profiles: ProfilePort
    ):
        self.file_facade = file_facade
        self.tokenizer = tokenizer
        self.classifier = classifier
        self.responder = responder
        self.profiles = profiles

    def execute_from_text(
        self,
        subject: str,
        body: str,
        sender: Optional[str] = None,
        profile_id: Optional[str] = None
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
            priority=profile.get("priority_keywords")
        )

        reply = self.responder.suggest(result, email)
        return type(result)(**{**result.__dict__, "suggested_reply": reply})

    def execute_from_file(
        self,
        filename: str,
        raw: bytes,
        profile_id: Optional[str] = None,
        subject: Optional[str] = None,
        sender: Optional[str] = None
    ) -> ClassificationResult:
        text = self.file_facade.from_upload(filename, raw)
        return self.execute_from_text(subject, text, sender, profile_id)
