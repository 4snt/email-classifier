import os
import json
import re
import http.client
from typing import List, Optional

from app.domain.entities import Email, ClassificationResult, Category
from app.domain.ports import ClassifierPort
from app.infrastructure.classifiers.rule_based import RuleBasedClassifier


TOOL_SCHEMA = [{
    "type": "function",
    "function": {
        "name": "emit",
        "description": "Retorne a classificação do e-mail.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["productive", "unproductive"]
                },
                "reason": {"type": "string"},
                "reply": {"type": "string", "description": "Vazio se unproductive/spam"}
            },
            "required": ["category", "reason", "reply"],
            "additionalProperties": False
        }
    }
}]


def _strip_signatures(text: str) -> str:
    if not text:
        return ""
    text = re.split(
        r"(?i)\n--\s*$|\nAtenciosamente,|\nKind regards,|\nBest regards,|\nEnviado do meu",
        text
    )[0]
    return text[:6000]


class OpenAIClassifier(ClassifierPort):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.escalation_model = os.getenv("OPENAI_MODEL_ESCALATE", "gpt-4.1-mini")
        self.rule_based = RuleBasedClassifier()
        self.gray_low = float(os.getenv("RB_GRAY_LOW", "0.45"))
        self.gray_high = float(os.getenv("RB_GRAY_HIGH", "0.75"))

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

        lang = (rb.extra or {}).get("lang", "pt")
        hits = (rb.extra or {}).get("profile_hits") or []
        rb_conf = float((rb.extra or {}).get("confidence", 0.0))

        # escala só na zona cinza
        model = self.default_model
        if self.gray_low <= rb_conf <= self.gray_high:
            model = self.escalation_model

        mood_instruction = f"- O tom da resposta deve ser {mood}." if mood else ""
        body_clip = _strip_signatures(email.body or "")

        priority_json = json.dumps(priority or [], ensure_ascii=False)
        hits_list = ", ".join(hits[:20]) if hits else "nenhum"

        system_msg = (
            "Você é um classificador de emails para priorização operacional. "
            "Siga estritamente o schema solicitado e não adicione campos extras."
        )

        user_prompt = f"""
Responda **exclusivamente** via chamada de função 'emit'.

Regras:
- "category" deve ser "productive" OU "unproductive".
- Se for promocional/newsletter/spam: "category" = "unproductive" e "reply" = "".
- "reason" deve ser curto e citar quando usar uma palavra de prioridade.
- "reply" (quando existir) deve estar no idioma: {lang}.
{mood_instruction}

Lista de palavras-chave prioritárias (com sinônimos). A presença delas é INDICADOR FORTE de que é produtivo:
priority_keywords = {priority_json}

Sinais do pré-processamento rule-based:
- hits: {hits_list}
- confiança rule-based: {rb_conf:.2f}

Email:
- Subject: {email.subject or ""}
- Sender: {email.sender or ""}
- Body (sem assinatura): {body_clip}
""".strip()

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt},
            ],
            "tools": TOOL_SCHEMA,
            "tool_choice": {"type": "function", "function": {"name": "emit"}},
            "temperature": 0.0,
            "max_tokens": 220,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            conn = http.client.HTTPSConnection("api.openai.com")
            conn.request("POST", "/v1/chat/completions", json.dumps(payload), headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            parsed = json.loads(data)
        except Exception:
            return rb

        if "error" in parsed:
            return rb

        usage = parsed.get("usage", {})

        # tool_calls primeiro
        choice = (parsed.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        tool_calls = msg.get("tool_calls") or []
        js = None

        if tool_calls:
            try:
                args = tool_calls[0]["function"]["arguments"]
                js = json.loads(args)
            except Exception:
                js = None

        # fallback para content bruto
        if js is None:
            content = (msg.get("content") or "").strip()
            content = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.S | re.I)
            match = re.search(r"\{.*\}", content, re.S)
            if match:
                try:
                    js = json.loads(match.group(0))
                except Exception:
                    js = None

        if not isinstance(js, dict):
            return rb

        # normalização
        cat_raw = str(js.get("category", "")).strip().lower()
        category = Category.PRODUCTIVE if cat_raw in ("productive", "produtivo") else Category.UNPRODUCTIVE
        reason = (js.get("reason") or "").strip() or "sem motivo"
        reply = (js.get("reply") or "").strip()
        if category == Category.UNPRODUCTIVE:
            reply = ""

        extra = dict(rb.extra or {})
        # boost na confiança se prioridade bateu
        if any(p.lower() in (email.body or "").lower() for p in (priority or [])):
            extra["priority_boost"] = True
            rb_conf = min(1.0, rb_conf + 0.15)

        extra.update({
            "llm": True,
            "rb_confidence": rb_conf,
            "hits": hits[:20],
            "model_effective": model,
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
