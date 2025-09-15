# app/interfaces/http/imap_router.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.infrastructure.email_sources.imap_service import ImapService
from app.infrastructure.email_sources.imap_adapter import ImapEmailSource
from app.bootstrap import build_use_case
from app.infrastructure.db import get_session

router = APIRouter(prefix="/imap", tags=["imap"])

imap_service: ImapService | None = None


class ImapConfig(BaseModel):
    host: str
    user: str
    password: str
    mailbox: str = "INBOX"
    profile_id: str = "default"
    interval: int = 60


@router.post("/config")
def configure_imap(cfg: ImapConfig, session: Session = Depends(get_session)):
    global imap_service
    if imap_service:
        imap_service.stop()

    source = ImapEmailSource(
        host=cfg.host,
        user=cfg.user,
        password=cfg.password,
        mailbox=cfg.mailbox,
    )

    uc = build_use_case()
    classifier = uc.classifier
    repo = uc.log_repo

    imap_service = ImapService(
        source=source,
        classifier=classifier,
        repo=repo,
        profile_id=cfg.profile_id,
        interval=cfg.interval,
    )
    imap_service.start()
    return {"status": "imap started", "profile_id": cfg.profile_id}


@router.get("/status")
def status_imap():
    if not imap_service:
        return {"status": "not configured"}
    return {"status": "running", "profile_id": imap_service.profile_id}


@router.post("/stop")
def stop_imap():
    global imap_service
    if imap_service:
        imap_service.stop()
        imap_service = None
        return {"status": "imap stopped"}
    raise HTTPException(status_code=400, detail="No IMAP service running")
