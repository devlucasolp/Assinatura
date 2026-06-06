"""
Cron jobs por instância.

Em vez de horários hardcoded, um job único roda a cada minuto e varre todas
as instâncias ativas, disparando briefings/polling cuja config bate com o
momento atual (HH:MM, timezone da instância).

Configuração lida de bots.instances:
  - briefing_morning, briefing_afternoon, briefing_evening (HH:MM ou NULL)
  - new_tasks_poll_minutes (int em minutos ou NULL)
  - briefing_timezone (IANA, ex: America/Sao_Paulo)
"""

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.context import current_instance
from core.logger import system_logger
from integrations.postgres import list_instances
from integrations.asana_client import get_my_tasks
from integrations.evolution_api import send_text_message
from bot.handlers.asana_query import _format_task_line

scheduler = AsyncIOScheduler()

# In-memory: marca o último HH:MM disparado por instância x slot, evita duplo envio no mesmo minuto
_last_fired: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Helpers de briefing
# ---------------------------------------------------------------------------

async def _morning_text(phone: str) -> str:
    overdue = await get_my_tasks(overdue_only=True)
    today   = await get_my_tasks(days_ahead=0)
    lines = ["🌅 *Bom dia! Resumo do seu Asana:*", ""]
    if overdue:
        lines.append(f"⚠️ *ATENÇÃO: {len(overdue)} tarefas atrasadas*")
        lines += [_format_task_line(t) for t in overdue[:10]]
        lines.append("")
    if today:
        lines.append(f"📅 *Para fechar hoje* ({len(today)}):")
        lines += [_format_task_line(t) for t in today]
    elif not overdue:
        lines.append("Sem pendências para hoje. Bom trabalho!")
    return "\n".join(lines)


async def _afternoon_text(phone: str) -> str:
    today = await get_my_tasks(days_ahead=0)
    lines = ["☕ *Resumo da tarde:*", ""]
    if today:
        lines.append(f"Ainda {len(today)} tarefas marcadas para hoje:")
        lines += [_format_task_line(t) for t in today]
    else:
        lines.append("Lista de hoje zerada!")
    return "\n".join(lines)


async def _evening_text(phone: str) -> str:
    today = await get_my_tasks(days_ahead=0)
    lines = ["🌇 *Fim do dia:*", ""]
    if today:
        lines.append("Ainda abertas para hoje:")
        lines += [_format_task_line(t) for t in today]
        lines.append("\nLembre de atualizar ou remarcar.")
    else:
        lines.append("Tudo limpo. Bom descanso!")
    return "\n".join(lines)


_SLOT_BUILDERS = {
    "morning":   _morning_text,
    "afternoon": _afternoon_text,
    "evening":   _evening_text,
}


# ---------------------------------------------------------------------------
# Loop principal (1x por minuto)
# ---------------------------------------------------------------------------

async def tick_briefings() -> None:
    """Varre instâncias ativas e dispara briefings cujo horário bateu agora."""
    instances = await list_instances()

    for inst in instances:
        if not inst.get("is_active"):
            continue

        phone = inst.get("phone_primary")
        if not phone:
            continue

        tz_name = inst.get("briefing_timezone") or "America/Sao_Paulo"
        try:
            now = datetime.now(ZoneInfo(tz_name))
        except Exception:
            now = datetime.now(timezone.utc)
        current_hhmm = now.strftime("%H:%M")

        for slot in ("morning", "afternoon", "evening"):
            scheduled = inst.get(f"briefing_{slot}")
            if not scheduled or scheduled != current_hhmm:
                continue

            fire_key = f"{inst['id']}:{slot}:{now.strftime('%Y-%m-%d')}"
            if _last_fired.get(inst["id"] + ":" + slot) == fire_key:
                continue
            _last_fired[inst["id"] + ":" + slot] = fire_key

            try:
                current_instance.set(inst)
                text = await _SLOT_BUILDERS[slot](phone)
                await send_text_message(to=phone, text=text, evolution_instance=inst["evolution_instance"])
                system_logger.info(f"[CRON] Briefing {slot} enviado | instance={inst['id']} phone={phone}")
            except Exception as e:
                system_logger.exception(f"[CRON] Falha em briefing {slot} de {inst['id']}: {e}")


# ---------------------------------------------------------------------------
# Polling de novas tarefas
# ---------------------------------------------------------------------------

_last_poll: dict[str, datetime] = {}


async def tick_new_tasks_poll() -> None:
    """Verifica novas tarefas para instâncias que ativaram polling."""
    instances = await list_instances()
    now = datetime.now(timezone.utc)

    for inst in instances:
        if not inst.get("is_active"):
            continue

        interval_min = inst.get("new_tasks_poll_minutes")
        if not interval_min:
            continue

        last = _last_poll.get(inst["id"])
        if last and (now - last) < timedelta(minutes=interval_min):
            continue

        _last_poll[inst["id"]] = now

        try:
            current_instance.set(inst)
            tasks = await get_my_tasks()
            if not tasks:
                continue

            window_start = now - timedelta(minutes=interval_min)
            new_tasks = []
            for task in tasks:
                created_at_str = task.get("created_at")
                if not created_at_str:
                    continue
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    if created_at > window_start:
                        new_tasks.append(task)
                except ValueError:
                    pass

            if new_tasks:
                lines = ["🚨 *Nova(s) tarefa(s) atribuída(s):*", ""]
                lines += [_format_task_line(t) for t in new_tasks]
                await send_text_message(
                    to=inst["phone_primary"],
                    text="\n".join(lines),
                    evolution_instance=inst["evolution_instance"],
                )
                system_logger.info(f"[CRON] {len(new_tasks)} nova(s) tarefa(s) notificada(s) | instance={inst['id']}")
        except Exception as e:
            system_logger.exception(f"[CRON] Falha em polling de {inst['id']}: {e}")


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

def start_scheduler():
    scheduler.add_job(tick_briefings,       IntervalTrigger(minutes=1), id="briefings")
    scheduler.add_job(tick_new_tasks_poll,  IntervalTrigger(minutes=1), id="new_tasks_poll")
    scheduler.start()
    system_logger.info("APScheduler iniciado (briefings + polling, varredura por minuto, config por instância)")


def shutdown_scheduler():
    scheduler.shutdown()
    system_logger.info("APScheduler encerrado.")
