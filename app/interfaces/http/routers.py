# app/interfaces/http/api_router.py
from fastapi import (
    APIRouter, UploadFile, File, Request,
    HTTPException, Depends
)
from sqlmodel import Session

from app.bootstrap import build_use_case
from app.application.dto import DirectJson, ClassifyResponse
from app.domain.errors import BadRequest
from app.ratelimiting import limiter
from app.infrastructure.db import get_session
from app.infrastructure.repositories.sql_log_repository import SqlLogRepository
from app.domain.entities import ClassificationLog

router = APIRouter()
uc = build_use_case()


@router.get("/health")
def health(request: Request):
    return {"status": "ok"}


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="Aceita JSON (subject/body + profile_id opcional) ou multipart com arquivo .pdf/.txt/.eml"
)
@limiter.limit("5/minute")
async def classify(
    request: Request,
    file: UploadFile | None = File(None),
):
    ctype = request.headers.get("content-type", "").lower()
    try:
        if "application/json" in ctype:
            data = await request.json()
            payload = DirectJson(**data)
            profile_id = payload.profile_id

            r = uc.execute_from_text(
                payload.subject,
                payload.body,
                payload.sender,
                profile_id=profile_id
            )
            return ClassifyResponse(**r.__dict__)

        if "multipart/form-data" in ctype:
            if not file:
                raise BadRequest("Envie 'file' (.pdf/.txt/.eml).")

            raw = await file.read()
            profile_id = request.query_params.get("profile_id")

            r = uc.execute_from_file(
                file.filename,
                raw,
                profile_id=profile_id,
            )
            return ClassifyResponse(**r.__dict__)

        raise BadRequest("Use JSON ou multipart/form-data.")

    except BadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/logs",
    response_model=list[ClassificationLog],
    summary="Lista os últimos logs de classificações"
)
def list_logs(
    limit: int = 50,
    session: Session = Depends(get_session),
):
    repo = SqlLogRepository(session)
    return repo.list_recent(limit=limit)
