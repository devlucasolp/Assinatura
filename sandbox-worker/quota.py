"""Rate limit por instância usando Redis (janela deslizante por minuto)."""

import logging
import time
from typing import Optional

import redis.asyncio as aioredis

from config import LIMITS, SETTINGS

log = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    global _redis
    if not SETTINGS.redis_url:
        return None
    if _redis is None:
        _redis = aioredis.from_url(SETTINGS.redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def check_and_increment(instance_id: str) -> tuple[bool, int]:
    """
    Retorna (permitido, contagem_atual).
    Se Redis não configurado, sempre permite (sem limite).
    """
    r = await get_redis()
    if r is None:
        return True, 0

    minute_bucket = int(time.time() // 60)
    key = f"sandbox:quota:{instance_id}:{minute_bucket}"

    try:
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 120)  # janela + folga
        count, _ = await pipe.execute()
    except Exception as e:
        log.warning(f"[QUOTA] Redis falhou: {e} — permitindo execução")
        return True, 0

    allowed = int(count) <= LIMITS.quota_per_minute
    if not allowed:
        log.info(f"[QUOTA] Bloqueado {instance_id}: {count}/{LIMITS.quota_per_minute}")
    return allowed, int(count)
