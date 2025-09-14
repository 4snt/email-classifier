from io import BytesIO
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from app.domain.ports import TextExtractorPort
from app.domain.errors import BadRequest

class PdfExtractor(TextExtractorPort):
    def extract(self, raw_bytes: bytes) -> str:
        try:
            with BytesIO(raw_bytes) as buf:
                reader = PdfReader(buf, strict=False)
                parts = []
                for page in reader.pages:
                    parts.append(page.extract_text() or "")
                text = "\n".join(parts).strip()
                if not text:
                    raise BadRequest("Não foi possível extrair texto do PDF (parece ser digitalizado).")
                return text
        except PdfReadError as e:
            raise BadRequest(f"PDF inválido: {e}")
        except Exception as e:
            raise BadRequest(f"Falha ao ler PDF: {e}")
