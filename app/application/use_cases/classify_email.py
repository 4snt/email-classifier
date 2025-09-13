from typing import Optional
from app.domain.entities import Email, ClassificationResult
from app.domain.ports import TokenizerPort, ClassifierPort, ReplySuggesterPort
from app.domain.errors import BadRequest

class FileFacade:
    """Converte upload (.pdf/.txt) para texto bruto."""
    def __init__(self, pdf_extractor, txt_extractor):
        self._pdf = pdf_extractor
        self._txt = txt_extractor

    def from_upload(self, filename: str, raw: bytes) -> str:
        name = (filename or "").lower()
        if name.endswith(".pdf"):  return self._pdf.extract(raw)
        if name.endswith(".txt"):  return self._txt.extract(raw)
        raise BadRequest("Supported files: .pdf or .txt")

class ClassifyEmailUseCase:
    def __init__(self, file_facade: FileFacade, tokenizer: TokenizerPort,
                 classifier: ClassifierPort, responder: ReplySuggesterPort):
        self.file_facade = file_facade
        self.tokenizer = tokenizer
        self.classifier = classifier
        self.responder = responder

    def execute_from_text(self, subject: Optional[str], body: str, sender: Optional[str]) -> ClassificationResult:
        email = Email(subject=subject, body=body, sender=sender)
        pre = self.tokenizer.preprocess(email.body)
        tokens = self.tokenizer.tokenize(pre)
        result = self.classifier.classify(email, tokens)
        reply = self.responder.suggest(result, email)
        return type(result)(**{**result.__dict__, "suggested_reply": reply})

    def execute_from_file(self, filename: str, raw: bytes, subject: Optional[str]=None, sender: Optional[str]=None) -> ClassificationResult:
        text = self.file_facade.from_upload(filename, raw)
        return self.execute_from_text(subject, text, sender)
