"""Persiste run em bots.sandbox_runs (Postgres compartilhado com o bot/Rails)."""

import logging
from typing import Optional

import asyncpg

from config import SETTINGS
from runner import RunResult

log = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None

CODE_MAX = 8 * 1024  # 8 KB


async def get_pool() -> Optional[asyncpg.Pool]:
    global _pool
    if not SETTINGS.postgres_url:
        return None
    if _pool is None:
        _pool = await asyncpg.create_pool(SETTINGS.postgres_url, min_size=1, max_size=4)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def save_run(*, instance_id: str, code: str, origin: str, result: RunResult) -> None:
    if not SETTINGS.log_runs:
        return
    pool = await get_pool()
    if pool is None:
        log.warning("[STORAGE] DATABASE_URL não configurado — run não persistida")
        return

    snippet = code if len(code) <= CODE_MAX else code[:CODE_MAX] + "\n[... truncated]"

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO bots.sandbox_runs (
                instance_id, code, stdout, stderr, exit_code,
                duration_ms, memory_peak_mb, killed, kill_reason, origin, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
            """,
            instance_id, snippet, result.stdout, result.stderr, result.exit_code,
            result.duration_ms, result.memory_peak_mb, result.killed, result.kill_reason, origin,
        )
