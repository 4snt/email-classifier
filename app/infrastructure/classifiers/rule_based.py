from typing import List, Optional, Set
import re

from app.domain.entities import Email, ClassificationResult, Category
from app.domain.ports import ClassifierPort

# --- detecção de idioma (pt/en/es) ----
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
except Exception:  # fallback se lib não estiver instalada
    detect = None

def detect_lang(text: str) -> str:
    if detect:
        try:
            lang = detect((text or "")[:4000])
            if lang in ("pt", "en", "es"):
                return lang
        except Exception:
            pass
    # heurística leve de fallback
    t = (text or "").lower()
    if any(w in t for w in (" você ", " obrigado", " nota fiscal", "prazo")):
        return "pt"
    if any(w in t for w in (" you ", " thanks", " invoice", "deadline", "meeting")):
        return "en"
    if any(w in t for w in (" usted ", " gracias", " factura", "plazo", "reunión")):
        return "es"
    return "pt"

# --- léxicos por idioma (genéricos) ---
PROD_PT: Set[str] = {
    "reunião","agenda","contrato","proposta","orçamento","prazo","entrega","fatura","boleto",
    "currículo","vaga","entrevista","suporte","pedido","pagamento","nf","nota","licitação","cotação"
}
PROD_EN: Set[str] = {
    "meeting","agenda","contract","proposal","quote","budget","deadline","delivery","invoice","bill",
    "resume","position","interview","support","order","payment","rfq","tender","sow"
}
PROD_ES: Set[str] = {
    "reunión","agenda","contrato","propuesta","presupuesto","plazo","entrega","factura",
    "currículum","vacante","entrevista","soporte","pedido","pago","licitación","cotización"
}

SPAM_COMMON: Set[str] = {
    "newsletter","spam","unsubscribe","descadastre-se","inscreva-se","click","clique","cupom","coupon",
    "frete","gratis","grátis","promo","promoção","desconto","oferta","sale","black","friday","ganhe",
    "aproveite","comprar","compre","ofertas"
}
SPAM_PT: Set[str] = {"promoção","desconto","oferta","newsletter","spam","inscreva-se","ganhe",
                     "cupom","marketing","frete","grátis","clique","aproveite","comprar","compre"}
SPAM_EN: Set[str] = {"promotion","discount","offer","newsletter","spam","subscribe","win","coupon",
                     "marketing","free","shipping","click","buy","sale","deal"}
SPAM_ES: Set[str] = {"promoción","descuento","oferta","boletín","spam","suscríbase","gane","cupón",
                     "marketing","envío","gratis","clic","comprar","rebaja","ofertas"}

_URL_RE = re.compile(r"https?://", re.I)

REASON_STRINGS = {
    "pt": {
        "spam": "conteúdo promocional/newsletter",
        "profile_hits": "palavras do perfil detectadas",
        "fallback_len": "fallback pelo tamanho do corpo",
        "neutral": "sem sinais fortes",
    },
    "en": {
        "spam": "promotional/newsletter content",
        "profile_hits": "profile keywords detected",
        "fallback_len": "fallback by body length",
        "neutral": "no strong signals",
    },
    "es": {
        "spam": "contenido promocional/boletín",
        "profile_hits": "palabras del perfil detectadas",
        "fallback_len": "criterio por extensión del cuerpo",
        "neutral": "sin señales fuertes",
    },
}

class RuleBasedClassifier(ClassifierPort):
    """
    Rule-based profile-aware, multilíngue (pt/en/es) + filtro de spam.
    - Usa priority (keywords+sinônimos) quando fornecido.
    - Detecta spam/anúncio por vocabulário + número de links.
    - Devolve 'extra' com 'lang', 'confidence', etc. para o responder adaptar a língua.
    """
    def classify(
        self,
        email: Email,
        tokens: List[str],
        mood: Optional[str] = None,
        priority: Optional[list[str]] = None,
    ) -> ClassificationResult:

        body = email.body or ""
        lang = detect_lang((email.subject or "") + "\n" + body)
        reasons = REASON_STRINGS.get(lang, REASON_STRINGS["pt"])

        # normaliza tokens
        tok_set = set((t or "").lower() for t in tokens)

        # --- SPAM / anúncio ---
        spam_vocab = SPAM_COMMON | (SPAM_PT if lang == "pt" else SPAM_EN if lang == "en" else SPAM_ES)
        spam_hits = tok_set.intersection(spam_vocab)
        link_count = len(_URL_RE.findall(body))

        if len(spam_hits) >= 2 or (len(spam_hits) >= 1 and link_count >= 2):
            reason = f"{reasons['spam']} (hits={len(spam_hits)}, links={link_count})"
            return ClassificationResult(
                category=Category.UNPRODUCTIVE,
                reason=reason,
                suggested_reply="",  # não responder spam
                used_model="rule-based",
                extra={
                    "lang": lang,
                    "is_spam": True,
                    "spam_hits": sorted(spam_hits),
                    "links": link_count,
                    "confidence": 0.9,
                },
            )

        # --- Produtivo por perfil (priority inclui sinônimos, vindo do use case) ---
        gen_prod = PROD_PT if lang == "pt" else PROD_EN if lang == "en" else PROD_ES
        prof_set = set(p.lower() for p in (priority or []))
        lexicon = prof_set if prof_set else gen_prod

        prod_hits = tok_set.intersection(lexicon)
        if prod_hits:
            conf = 0.55 + 0.1 * min(4, len(prod_hits))  # 0.55..0.95
            reason = f"{reasons['profile_hits']}: {', '.join(sorted(prod_hits))}"
            return ClassificationResult(
                category=Category.PRODUCTIVE,
                reason=reason,
                suggested_reply="",  # responder será gerado no responder com base em extra['lang']
                used_model="rule-based",
                extra={
                    "lang": lang,
                    "is_spam": False,
                    "profile_hits": sorted(prod_hits),
                    "confidence": min(conf, 0.9),
                },
            )

        # --- Fallback por tamanho ---
        if len(body) > 10_000:
            return ClassificationResult(
                category=Category.PRODUCTIVE,
                reason=reasons["fallback_len"],
                suggested_reply="",
                used_model="rule-based",
                extra={"lang": lang, "is_spam": False, "confidence": 0.55},
            )

        # --- Neutro → leve improdutivo (deixa SmartClassifier decidir se chama LLM) ---
        return ClassificationResult(
            category=Category.UNPRODUCTIVE,
            reason=reasons["neutral"],
            suggested_reply="",
            used_model="rule-based",
            extra={"lang": lang, "is_spam": False, "confidence": 0.5},
        )
