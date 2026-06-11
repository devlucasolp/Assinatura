"""
Integração com Redis — cache, sessões e controle de estado rápido.
Tolerante a falha: se o Redis estiver indisponível, erros são propagados pelo caller.

Convenção de chaves (multi-instância):
  bot:{instance_id}:status                   — status meeting/event/available
  bot:{instance_id}:auto_replied:{phone}      — debounce de auto-reply
  bot:{instance_id}:queue:{phone}             — fila de mensagens (debounce)
  bot:{instance_id}:debounce:{phone}          — janela de debounce ativa
  bot:{instance_id}:asana_pending:{phone}     — estado pendente de fluxo Asana
  bot:{instance_id}:last_task:{phone}         — última tarefa criada
  bot:{instance_id}:sent_msg:{message_id}     — echo-filter de mensagens enviadas
"""

import redis.asyncio as aioredis
from core.config import get_settings
from core.logger import redis_logger
from core.context import get_current_instance

settings = get_settings()
infra = settings.infra
storage = infra.storage
_REDIS_URL = storage.redis_url

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        redis_logger.info("Inicializando conexão com Redis")
        _redis = aioredis.from_url(
            _REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis.ping()
        redis_logger.info("Conexão com Redis estabelecida com sucesso")
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis:
        redis_logger.info("Fechando conexão com Redis")
        await _redis.aclose()
        _redis = None


async def set_key(key: str, value: str, expire_seconds: int | None = None) -> None:
    r = await get_redis()
    await r.set(key, value, ex=expire_seconds)
    redis_logger.debug(f"Redis SET | key: {key} | expire: {expire_seconds}s")


async def get_key(key: str) -> str | None:
    r = await get_redis()
    value = await r.get(key)
    redis_logger.debug(f"Redis GET | key: {key} | found: {value is not None}")
    return value


async def delete_key(key: str) -> None:
    r = await get_redis()
    await r.delete(key)
    redis_logger.debug(f"Redis DEL | key: {key}")


def _k(instance_id: str | None = None, *parts: str) -> str:
    """Monta uma chave Redis com namespace por instância."""
    if not instance_id:
        instance = get_current_instance()
        instance_id = instance.get("id", "default")
    return ":".join(["bot", instance_id, *parts])


async def set_meeting_status(status: str, duration_minutes: int | None = None, instance_id: str | None = None) -> None:
    """
    Define o status de indisponibilidade para uma instância.
    status: 'meeting' | 'event' | 'available'
    """
    r = await get_redis()
    key = _k(instance_id, "status")
    expire = duration_minutes * 60 if duration_minutes else None
    await r.set(key, status, ex=expire)
    redis_logger.info(f"Status atualizado | instance: {instance_id} | status: {status} | duração: {duration_minutes} min")


async def get_meeting_status(instance_id: str | None = None) -> str:
    """Retorna o status atual da instância. Padrão: 'available'"""
    r = await get_redis()
    status = await r.get(_k(instance_id, "status"))
    result = status or "available"
    redis_logger.debug(f"Status atual | instance: {instance_id} | status: {result}")
    return result


async def mark_auto_replied(phone: str, ttl_seconds: int = 3600, instance_id: str | None = None) -> None:
    """
    Marca que já enviamos auto-reply para este número nesta instância.
    Evita spam de mensagens automáticas repetidas. TTL padrão: 1 hora.
    """
    r = await get_redis()
    await r.set(_k(instance_id, "auto_replied", phone), "1", ex=ttl_seconds)
    redis_logger.debug(f"Auto-reply marcado | instance: {instance_id} | phone: {phone} | TTL: {ttl_seconds}s")


async def has_auto_replied(phone: str, instance_id: str | None = None) -> bool:
    """Verifica se já enviamos auto-reply para este número nesta instância."""
    r = await get_redis()
    return bool(await r.exists(_k(instance_id, "auto_replied", phone)))


# ---------------------------------------------------------------------------
# Debounce de mensagens - agrupa mensagens rápidas em uma única chamada ao LLM
# ---------------------------------------------------------------------------

DEBOUNCE_TTL = 4  # segundos de janela sem nova mensagem para disparar processamento


async def push_message_to_queue(phone: str, text: str, instance_id: str | None = None) -> None:
    """Adiciona mensagem à fila de debounce da instância/usuário."""
    r = await get_redis()
    key = _k(instance_id, "queue", phone)
    await r.rpush(key, text)
    await r.expire(key, 60)
    redis_logger.debug(f"Mensagem enfileirada | instance: {instance_id} | phone: {phone}")


async def set_debounce(phone: str, ttl: int = DEBOUNCE_TTL, instance_id: str | None = None) -> None:
    """Redefine o timer de debounce do usuário na instância."""
    r = await get_redis()
    await r.set(_k(instance_id, "debounce", phone), "1", ex=ttl)


async def debounce_active(phone: str, instance_id: str | None = None) -> bool:
    """Retorna True se ainda há mensagens chegando (janela ainda aberta)."""
    r = await get_redis()
    return bool(await r.exists(_k(instance_id, "debounce", phone)))


async def pop_all_queued_messages(phone: str, instance_id: str | None = None) -> list[str]:
    """Remove e retorna todas as mensagens acumuladas na fila."""
    r = await get_redis()
    key = _k(instance_id, "queue", phone)
    messages = await r.lrange(key, 0, -1)
    await r.delete(key)
    redis_logger.debug(f"{len(messages)} mensagens retiradas | instance: {instance_id} | phone: {phone}")
    return list(messages) if messages else []


# ---------------------------------------------------------------------------
# Estado pendente de ação Asana — mantém contexto entre mensagens
# ---------------------------------------------------------------------------

_ASANA_PENDING_TTL = 300  # 5 minutos para o usuário responder


async def save_asana_pending(phone: str, state: dict, instance_id: str | None = None) -> None:
    """
    Salva o estado pendente de uma ação Asana para a instância.
    state: {step, task_info, template, options, ...}
    """
    import json as _json
    r = await get_redis()
    await r.set(_k(instance_id, "asana_pending", phone), _json.dumps(state, ensure_ascii=False), ex=_ASANA_PENDING_TTL)
    redis_logger.debug(f"Estado pendente Asana salvo | instance: {instance_id} | phone: {phone} | step: {state.get('step')}")


async def get_asana_pending(phone: str, instance_id: str | None = None) -> dict | None:
    """Retorna o estado pendente de ação Asana ou None se não houver."""
    import json as _json
    r = await get_redis()
    raw = await r.get(_k(instance_id, "asana_pending", phone))
    if not raw:
        return None
    try:
        return _json.loads(raw)
    except Exception:
        return None


async def clear_asana_pending(phone: str, instance_id: str | None = None) -> None:
    """Remove o estado pendente após resolução."""
    r = await get_redis()
    await r.delete(_k(instance_id, "asana_pending", phone))
    redis_logger.debug(f"Estado pendente Asana removido | instance: {instance_id} | phone: {phone}")


# ---------------------------------------------------------------------------
# Última tarefa criada no Asana — permite recuperar link sem reinventar
# ---------------------------------------------------------------------------

_LAST_TASK_TTL = 86400  # 24 horas


async def save_last_task(phone: str, task: dict, instance_id: str | None = None) -> None:
    """
    Persiste os dados da última tarefa criada no Asana para este número/instância.
    task: {"name": str, "link": str | None, "project": str | None, "date": str | None}
    """
    import json as _json
    r = await get_redis()
    await r.set(_k(instance_id, "last_task", phone), _json.dumps(task), ex=_LAST_TASK_TTL)
    redis_logger.debug(f"Última tarefa salva | instance: {instance_id} | phone: {phone} | task: {task.get('name')}")


async def get_last_task(phone: str, instance_id: str | None = None) -> dict | None:
    """Retorna os dados da última tarefa criada para este número/instância, ou None."""
    import json as _json
    r = await get_redis()
    raw = await r.get(_k(instance_id, "last_task", phone))
    if not raw:
        return None
    try:
        return _json.loads(raw)
    except Exception:
        return None
