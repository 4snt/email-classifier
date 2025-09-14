import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.interfaces.http.routers import router
from app.ratelimiting import init_rate_limit  

app = FastAPI(title="Email Classifier (MVP enxuto)", version="0.1.0")

init_rate_limit(app)
app.include_router(router)

raw_origins = os.getenv("ALLOW_ORIGINS", "")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
