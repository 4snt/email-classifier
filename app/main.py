from fastapi import FastAPI
from app.interfaces.http.routers import router
from app.ratelimiting import init_rate_limit  

app = FastAPI(title="Email Classifier (MVP enxuto)", version="0.1.0")

init_rate_limit(app)

app.include_router(router)
