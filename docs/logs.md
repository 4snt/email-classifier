# 📑 Rota `/logs` — Histórico de Classificações

A rota `/logs` permite consultar os registros de classificações armazenados em **SQLite**.  
Serve para **auditoria**, **debug** e para facilitar os testes comparando respostas de diferentes modelos de IA.

---

## 🔌 Endpoint

- **GET** `/logs?limit=50`

### Parâmetros de Query
- `limit` *(opcional)*: número máximo de registros retornados (padrão: 50).

---

## 📤 Resposta

Exemplo de resposta:

```json
[
  {
    "id": 1,
    "created_at": "2025-09-14T15:17:01.032369",
    "source": "json",
    "subject": "Proposta, orçamento e cronograma — implantação do módulo Financeiro",
    "body_excerpt": "Olá, Murilo! Segue a proposta consolidada para a implantação do módulo Financeiro...",
    "sender": "cliente@empresa.com",
    "file_name": null,
    "profile_id": "default",
    "category": "productive",
    "reason": "mensagem relacionada a proposta, orçamento e cronograma",
    "suggested_reply": "Olá! Obrigado pelo contato. Recebemos sua mensagem e vamos prosseguir...",
    "used_model": "gpt-4.1-nano",
    "provider": "openai",
    "prompt_tokens": 279,
    "completion_tokens": 54,
    "total_tokens": 333,
    "cost_usd": 0.0,
    "latency_ms": null,
    "status": "ok",
    "error": null,
    "extra": null
  }
]
```

---

## ⚙️ Como funciona

- Cada chamada ao `POST /classify` gera um **log persistido** no SQLite (`app.db`).
- O log inclui:
  - dados de entrada (`subject`, `body_excerpt`, `sender`, `file_name`, `profile_id`)
  - resultado de classificação (`category`, `reason`, `suggested_reply`)
  - metadados do modelo (`used_model`, `provider`, `tokens`, `cost_usd`, `latency_ms`)
  - status e erros (se houver)

---

## 🎯 Casos de Uso

- Validar consistência das respostas entre **rule-based** e **LLM**.
- Testar **novos modelos** e comparar custo/latência.
- Auditar interações antes de integrar com sistemas externos.
