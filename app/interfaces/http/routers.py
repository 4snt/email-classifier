from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from app.application.dto import DirectJson, ClassifyResponse
from app.bootstrap import build_use_case
from app.domain.errors import BadRequest
from app.ratelimiting import limiter

router = APIRouter()
uc = build_use_case()

@limiter.limit("5/minute") 
@router.get("/health")
def health(request: Request):
    return {"status":"ok"}

@limiter.limit("5/minute") 
@router.post("/classify", response_model=ClassifyResponse,
             summary="Aceita JSON (subject/body) ou multipart com arquivo .pdf/.txt")
async def classify(request: Request, file: UploadFile | None = File(None)):
    ctype = request.headers.get("content-type","").lower()
    try:
        if "application/json" in ctype:
            data = await request.json()
            payload = DirectJson(**data)
            r = uc.execute_from_text(payload.subject, payload.body, payload.sender)
            return ClassifyResponse(**r.__dict__)
        if "multipart/form-data" in ctype:
            if not file:
                raise BadRequest("Envie 'file' (.pdf/.txt).")
            raw = await file.read()
            r = uc.execute_from_file(file.filename, raw)
            return ClassifyResponse(**r.__dict__)
        raise BadRequest("Use JSON ou multipart/form-data.")
    except BadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))
