# Email Classifier — MVP (FastAPI + DDD-lite)

MVP enxuto que recebe **texto direto** ou **arquivos (.pdf / .txt)**, normaliza para JSON, roda **NLP básico** (pré-process + tokenização), classifica o e-mail como **Produtivo** ou **Improdutivo** e gera uma **resposta sugerida**.  
Arquitetura **hexagonal** (ports & adapters), com **use case** único e adapters substituíveis (rule-based por padrão e LLM opcional).

---

## ✨ Features
- `POST /classify` aceita **JSON** ou **multipart** com arquivo `.pdf`/`.txt`  
- **Facade de arquivos** (PDF/TXT → texto)  
- **NLP** simples: lowercasing, remoção de stopwords, tokenização por regex  
- **Classificador**:
  - 🎯 **Rule-based** (padrão, sem custo)
  - 🤖 **OpenAI LLM** (opcional via `OPENAI_API_KEY`)
- **Resposta sugerida** automática e curta
- `GET /health` para monitoramento
- Swagger em `/docs`
- `GET /logs` para consultar histórico de classificações (armazenadas em SQLite)

---

## 🏗️ Arquitetura (Visão Lógica)

**Fluxo**  
1) **Entrada** → JSON direto *ou* upload `.pdf/.txt`  
2) **Facade Files** → extrai texto e normaliza  
3) **NLP** → `preprocess → tokenize`  
4) **Classifier** → rule-based (default) *ou* LLM  
5) **Responder** → mensagem curta coerente  
6) **Persistência** → registro no banco SQLite  
7) **Saída** → `category | reason | suggested_reply | tokens | custo`

**DDD + Hexagonal**  
- **Domain**: entidades (`Email`, `ClassificationResult`, `ClassificationLog`), portas (`TokenizerPort`, `ClassifierPort`, `ReplySuggesterPort`, `ProfilePort`, `LogRepositoryPort`), erros  
- **Application**: `ClassifyEmailUseCase` + `FileFacade`  
- **Infrastructure (adapters)**: extractors PDF/TXT, tokenizer simples, classifiers (rule-based, OpenAI), responder, repositórios SQL  
- **Interfaces**: HTTP (FastAPI routers)

---

## 📁 Estrutura de Pastas

```
email_classifier/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ bootstrap.py
│  ├─ interfaces/http/routers.py
│  ├─ application/
│  │   ├─ dto.py
│  │   └─ use_cases/classify_email.py
│  ├─ domain/
│  │   ├─ entities.py
│  │   ├─ ports.py
│  │   ├─ errors.py
│  │   └─ value_objects.py
│  └─ infrastructure/
│      ├─ extractors/
│      ├─ nlp/tokenizer_simple.py
│      ├─ classifiers/
│      ├─ responders/simple_templates.py
│      ├─ repositories/sql_log_repository.py
│      └─ models.py
├─ requirements.txt
├─ Dockerfile
└─ .env.example
```

---

## 📦 Dependências e Motivações

- **fastapi / uvicorn** → servidor web moderno e performático  
- **pydantic** → validação de entrada/saída  
- **python-multipart** → suporte a upload de arquivos  
- **pypdf** → leitura de PDFs textuais  
- **slowapi + limits** → rate limiting para proteção da API  
- **sqlalchemy + sqlmodel** → persistência simples em SQLite, modelo ORM enxuto  
- **sqlite** (via SQLModel) → banco leve, embarcado, ideal para logs temporários de classificação  
  - usado para **armazenar histórico de requisições** e testar diferentes modelos de IA com as mesmas entradas, ajudando a **afiar a IA** sem perder rastreabilidade  

---

## ▶️ Como Rodar (Local)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse:
- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

---

## 🔌 Endpoints

### `GET /health`
```json
{"status": "ok"}
```

### `POST /classify`
Aceita JSON ou arquivo (`.pdf` / `.txt`), normaliza, classifica e retorna resultado.

### `GET /logs`
Retorna histórico de classificações persistidas em SQLite.  
Exemplo:
```json
[
  {
    "id": 1,
    "created_at": "2025-09-14T15:17:01.032369",
    "subject": "Proposta e orçamento",
    "profile_id": "default",
    "category": "productive",
    "reason": "mensagem relacionada a proposta, orçamento e cronograma",
    "suggested_reply": "Olá! Obrigado pelo contato..."
  }
]
```

---

## 📍 Próximos passos

- Métricas de latência/custo direto no log  
- Testar diferentes LLMs em batch com o mesmo dataset (aproveitando o SQLite)  
- Criar painel para explorar os logs  
- Expandir NLP (stemming/lemmatização, multilíngue)  

---

## 📜 Licença
Uso livre neste desafio técnico. Se for publicar, considere **MIT**.
