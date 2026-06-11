"""
AUTH - Fluxo OAuth web do Google Drive (iniciado pelo dashboard Rails).

Responsabilidades deste módulo (Python):
  - Redirecionar para o consentimento Google
  - Receber o callback e trocar o code pelo token
  - Entregar o token ao Rails via POST /internal/connector_tokens
    (Rails é o único dono de bots.connector_tokens)

Variáveis necessárias no .env:
  OAUTH_SECRET              — senha para proteger a rota
  GOOGLE_CLIENT_ID          — OU credentials.json na raiz
  GOOGLE_CLIENT_SECRET      — OU credentials.json na raiz
  GOOGLE_OAUTH_REDIRECT_URI — URL de callback (ex: https://meubot.com/auth/drive/callback)
  RAILS_API_URL             — URL do Rails admin-api
  RAILS_BOT_SERVICE_KEY     — chave mestra do bot
"""

import json
import os
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from core.logger import app_logger

router = APIRouter(prefix="/auth", tags=["Auth"])

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

_RAILS_URL = os.getenv("RAILS_API_URL", "http://localhost:3000").rstrip("/")
_BOT_KEY   = os.getenv("RAILS_BOT_SERVICE_KEY", "")


def _make_flow(redirect_uri: str) -> Flow:
    creds_file = Path("credentials.json")
    if creds_file.exists():
        return Flow.from_client_secrets_file(
            str(creds_file), scopes=SCOPES, redirect_uri=redirect_uri
        )

    client_id     = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="credentials.json não encontrado e GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET não configurados",
        )

    return Flow.from_client_config(
        {
            "web": {
                "client_id":     client_id,
                "client_secret": client_secret,
                "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
                "token_uri":     "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )


def _redirect_uri(request: Request) -> str:
    override = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "")
    return override if override else str(request.url_for("callback_drive_oauth"))


async def _save_token_to_rails(token_dict: dict) -> None:
    """Entrega o token ao Rails — único dono de bots.connector_tokens."""
    if not _BOT_KEY:
        raise RuntimeError("RAILS_BOT_SERVICE_KEY não configurado")

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.post(
            f"{_RAILS_URL}/internal/connector_tokens",
            headers={"X-Bot-Service-Key": _BOT_KEY, "Content-Type": "application/json"},
            json={
                "connector":   "google_drive",
                "instance_id": "__global__",
                "token_data":  token_dict,
                "scope":       " ".join(SCOPES),
            },
        )

    if not res.is_success:
        raise RuntimeError(f"Rails respondeu {res.status_code}: {res.text}")


@router.get("/drive/status")
async def drive_status():
    """Consulta o Rails para saber se o token do Drive existe."""
    if not _BOT_KEY:
        return {"connected": False, "error": "RAILS_BOT_SERVICE_KEY não configurado"}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.get(
                f"{_RAILS_URL}/internal/tokens/google_drive",
                headers={"X-Bot-Service-Key": _BOT_KEY},
            )
        if res.status_code == 404:
            return {"connected": False}
        if res.is_success:
            data = res.json()
            return {"connected": True, "updated_at": data.get("updated_at")}
    except Exception as e:
        app_logger.warning(f"[AUTH] Falha ao consultar status do Drive no Rails: {e}")
    return {"connected": False}


@router.get("/drive")
async def start_drive_oauth(request: Request, secret: str = Query(default="")):
    """Inicia o fluxo OAuth do Google Drive."""
    expected = os.getenv("OAUTH_SECRET", "")
    if expected and secret != expected:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")

    if os.getenv("APP_ENV", "production") != "production":
        os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

    redirect_uri = _redirect_uri(request)
    flow = _make_flow(redirect_uri)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    app_logger.info(f"[AUTH] Iniciando OAuth Drive → {redirect_uri}")
    return RedirectResponse(auth_url)


@router.get("/drive/callback", name="callback_drive_oauth")
async def callback_drive_oauth(
    request: Request,
    code: str = Query(default=""),
    error: str = Query(default=""),
):
    """Recebe o callback do Google e entrega o token ao Rails."""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth negado: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Parâmetro 'code' ausente no callback")

    if os.getenv("APP_ENV", "production") != "production":
        os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

    redirect_uri = _redirect_uri(request)
    flow = _make_flow(redirect_uri)
    flow.fetch_token(code=code)
    token_dict = json.loads(flow.credentials.to_json())

    try:
        await _save_token_to_rails(token_dict)
        app_logger.info("[AUTH] Token do Google Drive entregue ao Rails")
    except Exception as e:
        app_logger.error(f"[AUTH] Falha ao salvar token no Rails: {e}")
        raise HTTPException(status_code=500, detail=f"Token obtido mas não foi possível salvar: {e}")

    return {"status": "ok", "message": "Google Drive autenticado! Pode fechar esta janela."}
