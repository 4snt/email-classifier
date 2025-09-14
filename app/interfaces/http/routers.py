import os
import jwt
from datetime import datetime, timedelta

from fastapi import (
    APIRouter, UploadFile, File, Request,
    HTTPException, Depends
)
from fastapi.security import HTTPBearer
from sqlmodel import Session

from app.application.dto import DirectJson, ClassifyResponse
from app.bootstrap import build_use_case
from app.domain.errors import BadRequest
from app.ratelimiting import limiter
from app.infrastructure.db import get_session
from app.infrastructure.repositories.sql_log_repository import SqlLogRepository
from app.infrastructure.repositories.user_repository import UserRepository  
from app.domain.entities import ClassificationLog, User
from app.application.dto import LoginResponse, LoginRequest

router = APIRouter()
uc = build_use_case()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)



def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(credentials=Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return payload



@limiter.limit("5/minute")
@router.get("/health")
def health(request: Request):
    return {"status": "ok"}


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Autentica usuário e retorna JWT"
)
def login(
    data: LoginRequest,
    session: Session = Depends(get_session)
):
    username = data.username
    password = data.password

    repo = UserRepository(session)
    user = repo.get_by_username(username)

    if not user or not repo.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="Aceita JSON (subject/body + profile_id opcional) ou multipart com arquivo .pdf/.txt/.eml"
)
@limiter.limit("5/minute")
async def classify(
    request: Request,
    file: UploadFile | None = File(None),
    user=Depends(get_current_user)  
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
    user=Depends(get_current_user) 
):
    repo = SqlLogRepository(session)
    return repo.list_recent(limit=limit)
