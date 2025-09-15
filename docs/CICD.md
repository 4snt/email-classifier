# 📧 Email Classifier MVP

Sistema web que classifica e-mails em **Produtivos** ou **Improdutivos** e sugere respostas automáticas.  
Projeto fullstack composto por **Frontend (Next.js + Tailwind)** e **Backend (FastAPI + Python)**, todo baseado em **Docker** e rodando em ambiente **self-hosted** com **Coolify** + **FRP**.

---

## 🚀 Deploy

### 📌 Arquitetura

- **Backend (FastAPI + Docker)**  
  Roda em servidor local via container, exposto por **FRP** através de um **VPS** (IONOS).  
  - Porta principal da API: `8000`
  - Documentação Swagger: `/docs`

- **Frontend (Next.js + Docker)**  
  Deploy realizado via **Coolify** em container separado, conectado ao backend através de endpoint exposto pelo FRP.  
  - Porta padrão: `3000` (interno) → exposto publicamente via domínio Coolify.

- **FRP (Fast Reverse Proxy)**  
  - `frps` no VPS (porta 7000 + proxies configurados).
  - `frpc` no servidor local para expor portas do backend.  
  Exemplo: `apiemailclassifier.flipafile.com` → redireciona para backend local.

---

## ⚙️ Passo a passo do Deploy

### 1. Backend (FastAPI)

1. Clonar o repositório:
   ```bash
   git clone https://github.com/4snt/email-classifier
   cd email-classifier
   ```

2. Configurar `.env`:
   ```env
   OPENAI_API_KEY=...
   ALLOW_ORIGINS=http://frontend-domain.com
   ```

3. Rodar com Docker:
   ```bash
   docker build -t email-classifier-backend .
   docker run -d --name email-backend -p 8000:8000 --env-file .env email-classifier-backend
   ```

4. Validar:
   ```
   http://localhost:8000/docs
   ```

---

### 2. FRP (exposição do backend)

📍 **No VPS (frps):**
```ini
[common]
bind_port = 7000
dashboard_port = 7500
token = TOKEN123
```

📍 **No servidor local (frpc):**
```ini
[common]
server_addr = vps.meudominio.com
server_port = 7000
token = TOKEN123

[email-api]
type = tcp
local_port = 8000
remote_port = 18000
```

➡️ Agora `http://vps.meudominio.com:18000/docs` acessa o backend local.

---

### 3. Frontend (Next.js via Coolify)

1. Conectar repositório do frontend no painel Coolify:
   ```
   https://github.com/4snt/email-classifier-frontend
   ```

2. Configurar variáveis no Coolify:
   ```env
   NEXT_PUBLIC_API_URL=https://apiemailclassifier.flipafile.com
   ```

3. Deploy automático pelo Coolify (build com Node + Docker).

4. Validar:
   ```
   https://autou.flipafile.com
   ```

---

### 4. Self-host + Integração

- Backend roda localmente em Docker.  
- FRP expõe o backend para o VPS.  
- Frontend em Coolify acessa via domínio público do VPS.  
- Painel do Coolify também é acessível via subdomínio seguro (porta 8443).

---

## 🖼️ Prints do Deploy

### 📌 Backend FastAPI
*(adicione aqui o print do container rodando no Docker / Swagger no navegador)*

---

### 📌 FRP (frps / frpc ativos)
*(adicione aqui o print do systemctl status e dashboard do FRP)*

---

### 📌 Coolify Deploy
*(adicione aqui o print do painel Coolify com os apps front/back rodando)*

---

### 📌 Frontend rodando
*(adicione aqui o print da aplicação em produção)*

---

## 🧩 Tecnologias

- **Backend:** Python 3.12 + FastAPI + Uvicorn  
- **Frontend:** Next.js 15 + React 18 + TailwindCSS 4  
- **Infra:** Docker + FRP + Coolify  
- **Hospedagem:** VPS IONOS + Servidor local (self-host)  

---

## ✨ Autor

Murilo Santiago Escobedo – [GitHub](https://github.com/4snt)  
