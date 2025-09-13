import re
from typing import List
from app.domain.ports import TokenizerPort

_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9_]+")

STOPWORDS = {
    "pt": {"a","o","as","os","de","do","da","para","por","e","ou","que","com","um","uma","em","no","na","nos","nas"},
    "en": {"a","the","to","for","and","or","of","in","on","is","are","be","with"}
}

class SimpleTokenizer(TokenizerPort):
    def __init__(self, lang: str = "pt"):
        self.stop = STOPWORDS.get(lang, set())

    def preprocess(self, text: str) -> str:
        return text.lower().strip()

    def tokenize(self, text: str) -> List[str]:
        return [t for t in _WORD_RE.findall(text) if t not in self.stop]
