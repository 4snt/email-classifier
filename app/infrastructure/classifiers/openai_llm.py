import os
import json
import re
import http.client
from typing import List, Optional

from app.domain.entities import Email, ClassificationResult, Category
from app.domain.ports import ClassifierPort
from app.infrastructure.classifiers.rule_based import RuleBasedClassifier


class OpenAIClassifier(ClassifierPort):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL")
        self.rule_based = RuleBasedClassifier()

    def classify(
        self,
        email: Email,
        tokens: List[str],
        mood: Optional[str] = None,
        priority: Optional[list[str]] = None
    ) -> ClassificationResult:
        rb = self.rule_based.classify(email, tokens, mood=mood, priority=priority)

        if not self.api_key or (rb.extra or {}).get("is_spam"):
            return rb

        model = self.default_model
        lang = (rb.extra or {}).get("lang", "pt")
        hits = (rb.extra or {}).get("profile_hits") or []
        rb_conf = float((rb.extra or {}).get("confidence", 0.0))

        mood_instruction = f"- O tom da resposta deve ser {mood}." if mood else ""
        priority_list = ", ".join(priority or [])
        hits_list = ", ".join(hits[:20]) if hits else "nenhum"
        body_clip = (email.body or "")[:4000]

        prompt = f"""
Você é um classificador de emails para priorização operacional. Responda SEMPRE em JSON válido.

Regras:
- Campo "category": "productive" OU "unproductive".
- Se for promocional/newsletter/spam: "category" = "unproductive" e "reply" = "" (vazio).
- Escreva "reason" curto e objetivo.
- A resposta (quando existir) deve estar no idioma detectado: {lang}.
{mood_instruction}
- Palavras-chave do perfil (com sinônimos): {priority_list}
- Sinais do pré-processamento (rule-based): {hits_list} (conf={rb_conf:.2f})

Email:
- Subject: {email.subject}
- Sender: {email.sender}
- Body (recorte): {body_clip}

Retorne APENAS um JSON com exatamente estes campos:
{{
  "category": "productive|unproductive",
  "reason": "string",
  "reply": "string (vazio se unproductive/spam)"
}}
""".strip()

        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 180
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 3) Chamada à API
        try:
            conn = http.client.HTTPSConnection("api.openai.com")
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            parsed = json.loads(data)
        except Exception:
            return rb

        if "error" in parsed:
            return rb

        choice = (parsed.get("choices") or [{}])[0]
        content = (choice.get("message") or {}).get("content", "").strip()
        usage = parsed.get("usage", {})

        # 4) Extrair apenas o JSON
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            content = match.group(0)

        try:
            js = json.loads(content)
            cat_raw = str(js.get("category", "")).strip().lower()
            category = Category.PRODUCTIVE if cat_raw in ("productive", "produtivo") else Category.UNPRODUCTIVE
            reason = (js.get("reason") or "").strip() or "sem motivo"
            reply = js.get("reply", "")
            if category == Category.UNPRODUCTIVE:
                reply = ""  # no-reply garantido para improdutivo/spam
        except Exception:
            return rb

        extra = dict(rb.extra or {})
        extra.update({
            "llm": True,
            "rb_confidence": rb_conf,
        })

        return ClassificationResult(
            category=category,
            reason=reason,
            suggested_reply=reply,
            total_tokens=usage.get("total_tokens"),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            used_model=model,
            extra=extra
        )
