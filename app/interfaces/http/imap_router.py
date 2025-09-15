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
    """
    Configura e inicia o serviço IMAP para leitura de e-mails.
    """
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
    """
    Retorna o status atual do serviço IMAP.
    """
    global imap_service
    if not imap_service:
        return {"status": "not configured"}
    return {
        "status": "running" if imap_service.is_running else "stopped",
        "profile_id": imap_service.profile_id,
        "interval": imap_service.interval,
        "mailbox": imap_service.source.mailbox,
        "host": imap_service.source.host,
    }


@router.post("/stop")
def stop_imap():
    """
    Interrompe o serviço IMAP se estiver em execução.
    """
    global imap_service
    if not imap_service:
        raise HTTPException(status_code=400, detail="No IMAP service running")

    imap_service.stop()
    imap_service = None
    return {"status": "imap stopped"}
