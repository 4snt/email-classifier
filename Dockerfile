# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=8044
ENV FORWARDED_ALLOW_IPS="*"

EXPOSE 8044

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]
