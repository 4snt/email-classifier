from fastapi import FastAPI
from app.interfaces.http.routers import router

app = FastAPI(title="Email Classifier (MVP enxuto)", version="0.1.0")
app.include_router(router)

