"""
Cliente do sandbox-worker — execução de código Python isolada.

Setado para uso em function calling do Gemini (PR 3) e admin (futuro).
"""

import os
from dataclasses import dataclass
from typing import Literal, Optional

import httpx

from core.logger import bot_logger

_WORKER_URL = os.getenv("SANDBOX_WORKER_URL", "http://sandbox-worker:8001").rstrip("/")
_BOT_KEY    = os.getenv("RAILS_BOT_SERVICE_KEY", "")    # mesma chave do Rails internal/

Origin = Literal["gemini", "admin", "test"]


@dataclass
class SandboxResult:
    stdout:          str
    stderr:          str
    exit_code:       int
    duration_ms:     int
    memory_peak_mb:  Optional[int]
    killed:          bool
    kill_reason:     Optional[str]
    error:           Optional[str]

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.error

    def to_llm_message(self) -> str:
        """Formata para enviar de volta ao LLM em function calling."""
        if self.error:
            return f"ERRO_WORKER: {self.error}"
        if self.killed:
            return f"ERRO_EXECUCAO: processo morto ({self.kill_reason})"
        if self.exit_code != 0:
            return f"ERRO_EXECUCAO (exit {self.exit_code}):\n{self.stderr}"
        out = self.stdout.strip() or "(sem output)"
        return out


async def execute_python(
    code: str,
    *,
    instance_id: str,
    origin: Origin = "gemini",
    timeout_seconds: int | None = None,
    memory_mb: int | None = None,
) -> SandboxResult:
    """Envia código ao sandbox-worker e retorna o resultado."""
    if not _BOT_KEY:
        return SandboxResult("", "", -1, 0, None, False, None,
                             error="RAILS_BOT_SERVICE_KEY não configurado no bot")

    payload = {
        "code":         code,
        "instance_id":  instance_id,
        "origin":       origin,
    }
    if timeout_seconds is not None:
        payload["timeout_seconds"] = timeout_seconds
    if memory_mb is not None:
        payload["memory_mb"] = memory_mb

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                f"{_WORKER_URL}/exec",
                json=payload,
                headers={"X-Bot-Service-Key": _BOT_KEY},
            )
    except httpx.RequestError as e:
        bot_logger.exception(f"[SANDBOX] Falha de rede ao worker: {e}")
        return SandboxResult("", "", -1, 0, None, False, None, error=f"worker_unreachable: {e}")

    if res.status_code != 200:
        return SandboxResult("", "", -1, 0, None, False, None,
                             error=f"worker_http_{res.status_code}: {res.text[:200]}")

    data = res.json()
    bot_logger.info(
        f"[SANDBOX] instance={instance_id} exit={data['exit_code']} "
        f"dur={data['duration_ms']}ms mem={data.get('memory_peak_mb')}MB"
        + (f" killed={data.get('kill_reason')}" if data.get('killed') else "")
    )
    return SandboxResult(**data)
