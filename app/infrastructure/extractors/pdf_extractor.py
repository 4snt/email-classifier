from io import BytesIO
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from app.domain.ports import TextExtractorPort
from app.domain.errors import BadRequest

class PdfExtractor(TextExtractorPort):
    def extract(self, raw_bytes: bytes) -> str:
        try:
            # pypdf precisa de um objeto com .seek() -> BytesIO resolve
            with BytesIO(raw_bytes) as buf:
                reader = PdfReader(buf, strict=False)
                parts = []
                for page in reader.pages:
                    # extract_text pode retornar None em páginas somente-imagem
                    parts.append(page.extract_text() or "")
                text = "\n".join(parts).strip()
                if not text:
                    # PDF provavelmente é digitalizado/scan sem camada de texto
                    raise BadRequest("Não foi possível extrair texto do PDF (parece ser digitalizado).")
                return text
        except PdfReadError as e:
            raise BadRequest(f"PDF inválido: {e}")
        except Exception as e:
            # fallback genérico para não vazar trace interno
            raise BadRequest(f"Falha ao ler PDF: {e}")
