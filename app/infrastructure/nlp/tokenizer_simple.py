import re
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # reproducibilidade

STOP_PT = {"de","da","do","a","o","e","que","em","para","com","um","uma","por","no","na","os","as"}
STOP_EN = {"the","a","an","and","of","to","in","for","on","with","is","are","be","this","that"}
STOP_ES = {"de","la","el","y","que","en","para","con","un","una","por","los","las","es","son"}

class SimpleTokenizer:
    def __init__(self, lang: str = "pt", supported_langs=("pt","en","es")):
        self.lang = lang
        self.supported_langs = supported_langs

    def preprocess(self, text: str) -> str:
        return (text or "").strip().lower()

    def tokenize(self, text: str):
        lang = self.lang
        if self.lang == "auto":
            try:
                guess = detect(text or "")
                lang = guess if guess in self.supported_langs else "pt"
            except Exception:
                lang = "pt"

        tokens = re.findall(r"\b\w+\b", text or "", flags=re.UNICODE)
        stop = STOP_PT if lang == "pt" else STOP_EN if lang == "en" else STOP_ES
        return [t for t in tokens if t not in stop]
