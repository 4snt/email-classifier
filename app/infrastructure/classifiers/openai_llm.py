import os
import json
import re
import http.client
from typing import List
from app.domain.entities import Email, ClassificationResult, Category
from app.domain.ports import ClassifierPort
from app.infrastructure.classifiers.rule_based import RuleBasedClassifier


class OpenAIClassifier(ClassifierPort):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
        self.rule_based = RuleBasedClassifier()

    def classify(
        self,
        email: Email,
        tokens: List[str],
        mood: str | None = None,
        priority: list[str] | None = None
    ) -> ClassificationResult:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        if not mood and not priority:
            model = "gpt-4.1-mini"
        else:
            model = "gpt-4.1-nano"

        conn = http.client.HTTPSConnection("api.openai.com")
        
        mood_instruction = f"- O tom da resposta deve ser {mood}." if mood else ""
        priority_instruction = (
            f"- Emails que devem ser considerados 'productive': {', '.join(priority)}."
            if priority else ""
        )

        prompt = f"""
Você é um classificador de emails.

Regras:
- Sempre responda em JSON válido, sem texto extra.
- A chave "category" deve ser EXATAMENTE "productive" ou "unproductive".
{mood_instruction}
{priority_instruction}

Exemplo 1:
{{
  "category": "productive",
  "reason": "candidato enviou currículo",
  "reply": "Thank you for your application. We will review your CV and get back to you soon."
}}

Exemplo 2:
{{
  "category": "unproductive",
  "reason": "conteúdo promocional",
  "reply": "sem resposta necessária"
}}

Agora analise o email abaixo e responda em JSON.

Email:
Subject: {email.subject}
Body: {email.body[:4000]}
"""

        payload = json.dumps({
            "model": model,   
            "messages": [{"role": "user", "content": prompt}]
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        parsed = json.loads(data)

        if "error" in parsed:
            return self.rule_based.classify(email, tokens)

        choice = parsed.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "").strip()

        usage = parsed.get("usage", {})

        # Extrair só o JSON da resposta
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            content = match.group(0)

        try:
            js = json.loads(content)
            cat_raw = js.get("category", "").strip().lower()

            if cat_raw in ["productive", "produtivo"]:
                category = Category.PRODUCTIVE
            else:
                category = Category.UNPRODUCTIVE

            reason = js.get("reason", "sem motivo")
            reply = js.get("reply", "sem resposta")

        except Exception:
            return self.rule_based.classify(email, tokens)

        return ClassificationResult(
        category=category,
        reason=reason,
        suggested_reply=reply,
        total_tokens=usage.get("total_tokens"),
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
        used_model=model   
    )
