class TxtExtractor:
    def extract(self, raw_bytes: bytes) -> str:
        # tenta utf-8 e fallback simples
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return raw_bytes.decode("latin-1", errors="ignore")
