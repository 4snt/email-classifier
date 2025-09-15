import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.interfaces.http.routers import router
from app.ratelimiting import init_rate_limit
from app.interfaces.http.imap_router import router as imap_router


app = FastAPI(
    title="Email Classifier (MVP)",  
    version="2.0.0"
)


init_rate_limit(app)


app.include_router(router)
app.include_router(imap_router)


raw_origins = os.getenv("ALLOW_ORIGINS", "")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

