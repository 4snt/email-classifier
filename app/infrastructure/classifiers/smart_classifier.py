from typing import List, Optional
from app.domain.entities import Email, ClassificationResult
from app.domain.ports import ClassifierPort

class SmartClassifier(ClassifierPort):
    """
    Combina rule-based (profile-aware) + LLM:
    - Se for spam → retorna rule-based (sem LLM).
    - Se confiança do rule-based >= min_conf → retorna rule-based.
    - Caso contrário, chama LLM com contexto do perfil/keywords e highlights.
    """
    def __init__(self, rule_based: ClassifierPort, llm: Optional[ClassifierPort], min_conf: float = 0.7):
        self.rule_based = rule_based
        self.llm = llm
        self.min_conf = min_conf

    def classify(
        self,
        email: Email,
        tokens: List[str],
        mood: Optional[str] = None,
        priority: Optional[list[str]] = None
    ) -> ClassificationResult:
        rb = self.rule_based.classify(email, tokens, mood=mood, priority=priority)
        extra = rb.extra or {}
        if extra.get("is_spam"):
            return rb  # sem LLM, economiza tokens

        if (extra.get("confidence") or 0.0) >= self.min_conf or self.llm is None:
            return rb

        # constrói um "highlight" simples para enriquecer o contexto do LLM
        tok_set = set(t.lower() for t in tokens)
        prof_set = set(p.lower() for p in (priority or []))
        hits = sorted(tok_set.intersection(prof_set))[:20]

        # Chama o LLM com as mesmas entradas + perfil expandido
        llm_res = self.llm.classify(
            email=email,
            tokens=tokens,
            mood=mood,
            priority=list(prof_set) if prof_set else None
        )

        # mescla informações úteis do rule-based
        merged_extra = {**(llm_res.extra or {}), "rb_hits": hits, "rb_confidence": extra.get("confidence")}
        return type(llm_res)(**{**llm_res.__dict__, "extra": merged_extra})
