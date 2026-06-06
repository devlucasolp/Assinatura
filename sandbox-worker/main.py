"""
Sandbox worker — FastAPI que recebe código Python e o roda em container efêmero.

Autenticação: header X-Bot-Service-Key (mesma chave que o Rails expõe internamente).
Roda em rede interna do compose — não expor publicamente.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, field_validator

from config import LIMITS, SETTINGS
from runner import run_code
from storage import close_pool, save_run
from quota import check_and_increment, close_redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s")
log = logging.getLogger("sandbox-worker")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

Origin = Literal["gemini", "admin", "test"]


class ExecRequest(BaseModel):
    code:             str = Field(..., min_length=1, max_length=64_000)
    instance_id:      str = Field(..., min_length=1, max_length=200)
    origin:           Origin = "gemini"
    timeout_seconds:  int | None = Field(default=None, ge=1, le=LIMITS.timeout_seconds)
    memory_mb:        int | None = Field(default=None, ge=16, le=LIMITS.memory_mb)
    cpus:             float | None = Field(default=None, gt=0, le=LIMITS.cpus)

    @field_validator("code")
    @classmethod
    def strip_code(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("code não pode ser vazio")
        return v


class ExecResponse(BaseModel):
    stdout:          str
    stderr:          str
    exit_code:       int
    duration_ms:     int
    memory_peak_mb:  int | None
    killed:          bool
    kill_reason:     str | None
    error:           str | None


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("=" * 60)
    log.info("  Sandbox Worker iniciando")
    log.info(f"  Imagem: {SETTINGS.sandbox_image}")
    log.info(f"  Limites: timeout={LIMITS.timeout_seconds}s mem={LIMITS.memory_mb}MB cpu={LIMITS.cpus}")
    log.info(f"  Postgres logging: {'on' if SETTINGS.postgres_url and SETTINGS.log_runs else 'off'}")
    log.info("=" * 60)
    if not SETTINGS.bot_service_key:
        log.warning("[BOOT] BOT_SERVICE_KEY não configurado — endpoint /exec aceita qualquer chave")
    yield
    await close_pool()
    await close_redis()


app = FastAPI(title="Sandbox Worker", version="0.1.0", lifespan=lifespan)


def _check_auth(provided: str | None) -> None:
    expected = SETTINGS.bot_service_key
    if not expected:
        return  # dev mode — sem chave configurada
    if not provided or provided != expected:
        raise HTTPException(status_code=401, detail="Chave de serviço inválida")


@app.get("/health")
async def health():
    return {"status": "ok", "image": SETTINGS.sandbox_image}


@app.post("/exec", response_model=ExecResponse)
async def exec_code(
    req: ExecRequest,
    x_bot_service_key: str | None = Header(default=None, alias="X-Bot-Service-Key"),
):
    _check_auth(x_bot_service_key)

    allowed, count = await check_and_increment(req.instance_id)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Quota por minuto excedida ({count}/{LIMITS.quota_per_minute})",
        )

    # Container Docker é sync — rodamos em executor
    result = await asyncio.to_thread(
        run_code,
        req.code,
        instance_id=req.instance_id,
        timeout_seconds=req.timeout_seconds,
        memory_mb=req.memory_mb,
        cpus=req.cpus,
    )

    # Persistir em background, não bloqueia resposta
    asyncio.create_task(
        save_run(instance_id=req.instance_id, code=req.code, origin=req.origin, result=result)
    )

    return ExecResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        memory_peak_mb=result.memory_peak_mb,
        killed=result.killed,
        kill_reason=result.kill_reason,
        error=result.error,
    )
