# 📧 Email Classifier — Backend (FastAPI + DDD-lite)

MVP enxuto para **classificação automática de e-mails**.  
Recebe **texto direto**, **arquivos (.pdf / .txt)** ou lê diretamente de uma **caixa de entrada IMAP**,  
classifica o e-mail como **Produtivo** ou **Improdutivo** e gera uma **resposta sugerida**.

Arquitetura **hexagonal** (ports & adapters), com **use cases** independentes e adapters substituíveis.  
Por padrão usa classificador **rule-based**, mas é possível plugar **LLMs** (ex: OpenAI).

---

## ✨ Features

- `POST /classify`  
  Aceita **JSON** ou **multipart** (`.pdf` / `.txt`)  
- **Facade de arquivos** (PDF/TXT → texto)  
- **NLP simples**: lowercasing, stopwords, tokenização regex  
- **Classificação**:
  - 🎯 Rule-based (padrão, sem custo)
  - 🤖 OpenAI LLM (opcional via `OPENAI_API_KEY`)
- **Resposta sugerida** curta e automática  
- **Logs** persistidos em SQLite  
- **IMAP Service**:
  - `POST /imap/config` → conecta na caixa de entrada  
  - `GET /imap/status` → status do serviço  
  - `POST /imap/stop` → encerra o worker IMAP  
  - Worker em thread (`ImapService`) que classifica periodicamente novos e-mails
- Swagger em `/docs`  
- `GET /health` para monitoramento  

---

## 🏗️ Arquitetura (Visão Lógica)

**Fluxo via IMAP**
1. Front envia `host, user, senha_app, mailbox, profile_id`  
2. Backend sobe um **worker (thread)** com `ImapService`  
3. Worker chama `SyncEmailsUseCase.run()` periodicamente  
4. Cada e-mail:
   - Tokenização → Classificação  
   - Log persistido em SQLite  
   - Mensagem movida para pasta (`Produtivos` ou `Improdutivos`)  

---

## 📁 Estrutura de Pastas

```bash
email_classifier/
├─ app/
│  ├─ main.py                  # inicialização FastAPI
│  ├─ config.py                # configs/env
│  ├─ bootstrap.py             # DI bootstrap
│  ├─ interfaces/http/         # rotas HTTP
│  │   ├─ classify_router.py
│  │   ├─ logs_router.py
│  │   └─ imap_router.py       # rotas /imap/*
│  ├─ application/
│  │   └─ use_cases/
│  │        ├─ classify_email.py
│  │        └─ sync_emails.py  # UseCase IMAP
│  ├─ domain/
│  │   ├─ entities.py
│  │   ├─ ports.py
│  │   └─ value_objects.py
│  └─ infrastructure/
│      ├─ email_sources/
│      │   ├─ imap_adapter.py  # adapter IMAP
│      │   └─ imap_service.py  # worker com start/stop
│      ├─ nlp/tokenizer_simple.py
│      ├─ classifiers/
│      ├─ responders/
│      └─ repositories/sql_log_repository.py
├─ requirements.txt
├─ Dockerfile
└─ .env.example
```

---

## 📦 Dependências

- **fastapi / uvicorn** → API moderna  
- **pydantic** → validação  
- **sqlalchemy + sqlmodel** → persistência (SQLite)  
- **imaplib** → integração IMAP  
- **pypdf** → parsing de PDF  
- **python-multipart** → upload de arquivos  
- **slowapi** → rate limiting  

---

## ▶️ Como Rodar (Local)

### 1. Backend
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend (Next.js)
```bash
cd email-classifier-frontend
pnpm dev
```

> Defina `NEXT_PUBLIC_API_URL=http://localhost:8000`

---

## 🔌 Endpoints

### Health
`GET /health`
```json
{"status": "ok"}
```

### Classificação manual
`POST /classify` → via JSON ou upload (`.pdf/.txt`)

### Logs
`GET /logs` → histórico em SQLite

### IMAP
- `POST /imap/config` → inicia serviço IMAP  
- `GET /imap/status` → status atual  
- `POST /imap/stop` → encerra serviço  

---

## 🧪 Exemplo — Iniciar IMAP

```bash
curl -X POST http://127.0.0.1:8000/imap/config   -H "Content-Type: application/json"   -d '{
    "host": "imap.gmail.com",
    "user": "seuemail@gmail.com",
    "password": "senha_app_google",
    "mailbox": "INBOX",
    "profile_id": "default",
    "interval": 10
  }'
```

Resposta:
```json
{
  "status": "imap running",
  "profile_id": "default",
  "host": "imap.gmail.com",
  "mailbox": "INBOX",
  "interval": 10
}
```

---

## 📍 Roadmap Futuro

- Métricas de custo/latência em cada log  
- Dashboard web para explorar logs  
- Suporte multi-conta IMAP  
- Stemming, lematização e multilíngue  
- Plug-and-play para outros LLMs  

---

## 📜 Licença
MIT — uso livre para protótipos e estudo.
