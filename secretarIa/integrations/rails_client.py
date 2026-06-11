"""
Cliente HTTP para o Rails admin-api.
O Python nunca escreve em bots.* diretamente — delega ao Rails via este cliente.
"""

import asyncio
import os
import httpx

from core.logger import bot_logger

_RAILS_URL = os.getenv("RAILS_API_URL", "http://localhost:3000")
_BOT_KEY   = os.getenv("RAILS_BOT_SERVICE_KEY", "")


def _headers() -> dict:
    if not _BOT_KEY:
        raise RuntimeError("RAILS_BOT_SERVICE_KEY não configurado no .env")
    return {"X-Bot-Service-Key": _BOT_KEY, "Content-Type": "application/json"}


async def get_token(connector: str, instance_id: str = "__global__") -> dict:
    """
    Retorna o token fresco de um conector.
    O Rails faz refresh automaticamente se expirado.
    """
    if instance_id == "__global__":
        url = f"{_RAILS_URL}/internal/tokens/{connector}"
    else:
        url = f"{_RAILS_URL}/internal/tokens/{connector}/{instance_id}"

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(url, headers=_headers())

    if res.status_code == 404:
        raise FileNotFoundError(f"Token '{connector}' não encontrado. Configure o conector no dashboard.")
    if res.status_code == 401:
        raise PermissionError("RAILS_BOT_SERVICE_KEY inválida ou não configurada.")
    res.raise_for_status()

    data = res.json()
    bot_logger.debug(f"[RAILS] Token obtido | connector: {connector} | instance: {instance_id}")
    return data["token_data"]


async def get_all_tokens() -> list[dict]:
    """Retorna todos os tokens ativos de uma vez."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{_RAILS_URL}/internal/tokens", headers=_headers())
    res.raise_for_status()
    return res.json()["tokens"]


def get_token_sync(connector: str, instance_id: str = "__global__") -> dict:
    """Versão síncrona para uso em contextos não-async (ex: _load_creds do Drive)."""
    return asyncio.get_event_loop().run_until_complete(get_token(connector, instance_id))
