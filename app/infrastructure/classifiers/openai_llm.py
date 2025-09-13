import os
from typing import List
from app.domain.entities import Email, ClassificationResult, Category
from app.domain.ports import ClassifierPort
import json, http.client

class OpenAIClassifier(ClassifierPort):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model

    def classify(self, email: Email, tokens: List[str]) -> ClassificationResult:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        # chamada HTTP mínima (sem SDK) p/ não adicionar dependências
        conn = http.client.HTTPSConnection("api.openai.com")
        prompt = (
            "Classifique este email como 'productive' ou 'unproductive' e dê um motivo curto.\n"
            f"Subject: {email.subject}\nBody: {email.body[:4000]}"
        )
        payload = json.dumps({"model": self.model, "messages":[{"role":"user","content":prompt}]})
        headers = {"Content-Type":"application/json","Authorization":f"Bearer {self.api_key}"}
        conn.request("POST","/v1/chat/completions",payload,headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        text = json.loads(data)["choices"][0]["message"]["content"].lower()
        category = Category.PRODUCTIVE if "productive" in text or "produtivo" in text else Category.UNPRODUCTIVE
        reason = text[:200].strip()
        return ClassificationResult(category, 0.8, reason)
