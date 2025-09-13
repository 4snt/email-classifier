# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Porta padrão do app (pode sobrescrever com -e PORT=xxxx)
ENV PYTHONUNBUFFERED=1
ENV PORT=8044

EXPOSE 8044
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
