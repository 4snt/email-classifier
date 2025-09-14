from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup

class EmlExtractor:
    def extract(self, raw_bytes: bytes) -> str:
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

        texts_plain = []
        texts_html = []

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = (part.get_content_disposition() or "").lower()
                if disp == "attachment":
                    continue
                if ctype == "text/plain":
                    texts_plain.append(part.get_content())
                elif ctype == "text/html":
                    texts_html.append(self._html_to_text(part.get_content()))
        else:
            ctype = msg.get_content_type()
            if ctype == "text/plain":
                texts_plain.append(msg.get_content())
            elif ctype == "text/html":
                texts_html.append(self._html_to_text(msg.get_content()))

        text = "\n\n".join(t.strip() for t in texts_plain if t and t.strip())
        if not text:
            text = "\n\n".join(t.strip() for t in texts_html if t and t.strip())

        text = self._strip_signature_and_quotes(text)
        return text.strip()

    def _html_to_text(self, html: str) -> str:
        soup = BeautifulSoup(html or "", "html.parser")
        return soup.get_text(separator="\n")

    def _strip_signature_and_quotes(self, text: str) -> str:
        lines = (text or "").splitlines()
        cleaned = []
        for ln in lines:
            if ln.strip().startswith(">"):
                continue
            cleaned.append(ln)
        joined = "\n".join(cleaned)
        if "\n-- " in joined:
            joined = joined.split("\n-- ", 1)[0]
        return joined
