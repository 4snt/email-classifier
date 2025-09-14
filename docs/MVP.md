# Email Classifier — MVP (FastAPI + DDD-lite)

MVP **enxuto** para classificar e-mails como **Produtivo** ou **Improdutivo** e gerar uma **resposta sugerida**.
Entrada pode ser **JSON** (subject/body) ou **arquivo** `.pdf`/`.txt`. Arquitetura **hexagonal** (ports/adapters) com use case único.

## ✨ Entregas do MVP

- `POST /classify` aceita **JSON** e **multipart** (`.pdf`/`.txt`)
- **NLP básico** (preprocess + tokenização + stopwords PT/EN)
- **Classificador rule-based** (padrão) | **LLM opcional** via `OPENAI_API_KEY`
- **Resposta sugerida** conforme categoria
- `GET /health` | Swagger em `/docs`

## Estrutura de Arquivos do MVP

- app
  ├── application
  │ ├── dto.py
  │ └── use_cases
  │ └── classify_email.py
  ├── bootstrap.py
  ├── config.py
  ├── data
  │ └── profiles.json
  ├── domain
  │ ├── entities.py
  │ ├── errors.py
  │ └── ports.py
  ├── infrastructure
  │ ├── classifiers
  │ │ ├── openai_llm.py
  │ │ └── rule_based.py
  │ ├── extractors
  │ │ ├── direct_json.py
  │ │ ├── pdf_extractor.py
  │ │ └── txt_extractor.py
  │ ├── nlp
  │ │ └── tokenizer_simple.py
  │ ├── profiles
  │ │ └── profile_json.py
  │ └── responders
  │ └── simple_templates.py
  ├── interfaces
  │ └── http
  │ └── routers.py
  ├── main.py
  └── ratelimiting.py

  13 directories, 19 files

## 🚀 Rodar

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# API: http://127.0.0.1:8000  |  Docs: http://127.0.0.1:8000/docs
```

> Para usar LLM, exporte `OPENAI_API_KEY` **antes** de iniciar.

### Docker

```bash
docker build -t email-classifier:latest .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY email-classifier:latest
```

## 🔌 Endpoints

- `GET /health` → `{ "status": "ok" }`
- `POST /classify` (JSON): `{"subject":"...", "body":"...", "sender":"..."}`
- `POST /classify` (arquivo): `-F "file=@/caminho/email.txt|.pdf"`

## 🧱 Estrutura

```
app/
  main.py | bootstrap.py
  application/ (use_cases/)
  domain/ (entities, ports, errors)
  infrastructure/ (extractors, nlp, classifiers, responders)
```

## ⚙️ Config

- `.env.example` inclui `OPENAI_API_KEY=` (opcional). Sem LLM → usa rule-based.

## 📍 Próximos passos

- Pesos e testes no rule-based
- OCR para PDFs escaneados
- Métricas/logs e CI no GitHub Actions

## 📄 Licença

Definir (ex.: MIT) ao publicar.
