import os
import json, http.client
from typing import List
from app.domain.entities import Email, ClassificationResult, Category
from app.domain.ports import ClassifierPort
from app.infrastructure.classifiers.rule_based import RuleBasedClassifier


class OpenAIClassifier(ClassifierPort):
    def __init__(self, model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.rule_based = RuleBasedClassifier()

    def classify(self, email: Email, tokens: List[str]) -> ClassificationResult:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        conn = http.client.HTTPSConnection("api.openai.com")

        # 🔒 forçar JSON para evitar confusão
        prompt = f"""
Responda APENAS neste JSON, sem comentários:
{{
  "category": "productive" | "unproductive",
  "reason": "motivo curto",
  "reply": "resposta curta e educada"
}}

Email:
Subject: {email.subject}
Body: {email.body[:4000]}
        """

        payload = json.dumps({
            "model": self.model,
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
            # fallback pro rule-based se a API falhar
            return self.rule_based.classify(email, tokens)

        choice = parsed.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "").strip()

        usage = parsed.get("usage", {})

        try:
            js = json.loads(content)
            category = (
                Category.PRODUCTIVE
                if js.get("category") in ["productive", "produtivo"]
                else Category.UNPRODUCTIVE
            )
            reason = js.get("reason", "sem motivo")
            reply = js.get("reply", "sem resposta")
        except Exception:
            # fallback se não for JSON válido
            return self.rule_based.classify(email, tokens)

        return ClassificationResult(
            category=category,
            confidence=0.9,
            reason=reason,
            suggested_reply=reply,
            total_tokens=usage.get("total_tokens"),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )
