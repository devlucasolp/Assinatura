"""
SYSTEM - Rotas de controle do sistema (ativar/desativar modo reunião/evento)
Estas rotas permitem controle manual ou via automação externa (ex: Google Calendar webhook)
"""

from datetime import date
from fastapi import APIRouter, Body, Query
from core.logger import system_logger, get_log_buffer
from integrations.redis_client import get_meeting_status
from core.context import current_instance
from integrations.postgres import get_instance

router = APIRouter(prefix="/system")


from system.handlers.meeting_notify import (
    set_status_meeting,
    set_status_event,
    set_status_available,
)

@router.post("/{instance_id}/status/meeting")
async def activate_meeting_mode(instance_id: str, duration_minutes: int | None = Body(default=None, embed=True)):
    """Ativa modo reunião - auto-reply para quem enviar mensagem."""
    system_logger.info(f"[SYSTEM] API: Ativando modo reunião | instance: {instance_id} | duração: {duration_minutes} min")
    
    inst = await get_instance(instance_id)
    if inst:
        current_instance.set(inst)
    
    await set_status_meeting(duration_minutes)
    return {"status": "meeting", "duration_minutes": duration_minutes}


@router.post("/{instance_id}/status/event")
async def activate_event_mode(instance_id: str, duration_minutes: int | None = Body(default=None, embed=True)):
    """Ativa modo evento - auto-reply para quem enviar mensagem."""
    system_logger.info(f"[SYSTEM] API: Ativando modo evento | instance: {instance_id} | duração: {duration_minutes} min")
    
    inst = await get_instance(instance_id)
    if inst:
        current_instance.set(inst)
        
    await set_status_event(duration_minutes)
    return {"status": "event", "duration_minutes": duration_minutes}


@router.post("/{instance_id}/status/available")
async def activate_available_mode(instance_id: str):
    """Desativa qualquer modo - Gabi volta a responder normalmente."""
    system_logger.info(f"[SYSTEM] API: Instância marcada como disponível | instance: {instance_id}")
    
    inst = await get_instance(instance_id)
    if inst:
        current_instance.set(inst)
        
    await set_status_available()
    return {"status": "available"}


@router.get("/{instance_id}/status")
async def get_current_status(instance_id: str):
    """Retorna o status atual de uma instância."""
    inst = await get_instance(instance_id)
    if inst:
        current_instance.set(inst)
    status = await get_meeting_status()
    system_logger.debug(f"[SYSTEM] API: Status consultado = {status} | instance: {instance_id}")
    return {"status": status}


@router.post("/{instance_id}/notify/daily")
async def notify_daily_brief(instance_id: str):
    """
    Envia o briefing diário do Asana para o telefone de uma instância via WhatsApp.
    Inclui: tarefas atrasadas + tarefas com vencimento hoje e amanhã.
    """
    from integrations.asana_client import get_tasks_due_soon, get_overdue_tasks
    from integrations.evolution_api import send_text_message
    
    inst = await get_instance(instance_id)
    if not inst:
        return {"error": "Instância não encontrada"}
        
    current_instance.set(inst)
    phone = inst.get("phone_primary")

    if not phone:
        return {"error": "Telefone primário não configurado nesta instância"}

    system_logger.info(f"[SYSTEM] Enviando briefing diário para {phone} | instance: {instance_id}")

    today_str = date.today().strftime("%d/%m/%Y")
    overdue = await get_overdue_tasks()
    due_soon = await get_tasks_due_soon(days_ahead=1)

    sections = [f"*Briefing do dia — {today_str}*"]

    if overdue:
        lines = [f"\n⚠️ *Atrasadas* ({len(overdue)}):"]
        for t in overdue[:10]:
            d = t.get("due_on", "")
            try:
                d = date.fromisoformat(d).strftime("%d/%m") if d else "—"
            except ValueError:
                pass
            lines.append(f"• {t['name']} ({d})")
        sections.append("\n".join(lines))

    if due_soon:
        lines = [f"\n📅 *Vencendo hoje/amanhã* ({len(due_soon)}):"]
        for t in due_soon[:10]:
            d = t.get("due_on", "")
            try:
                d = date.fromisoformat(d).strftime("%d/%m") if d else "—"
            except ValueError:
                pass
            lines.append(f"• {t['name']} ({d})")
        sections.append("\n".join(lines))

    if len(sections) == 1:
        sections.append("\nNada com prazo para hoje ou amanhã. 👍")

    await send_text_message(to=phone, text="\n".join(sections), evolution_instance=inst.get("evolution_instance"))
    system_logger.info("[SYSTEM] Briefing diário enviado")
    return {"status": "sent", "overdue": len(overdue), "due_soon": len(due_soon)}


@router.get("/logs")
async def get_logs(
    source: str | None = Query(default=None, description="Filtrar por fonte: ASANA, BOT, WEBHOOK, etc."),
    level: str | None = Query(default=None, description="Filtrar por nível: DEBUG, INFO, WARNING, ERROR"),
    tail: int = Query(default=100, le=500, description="Últimas N entradas"),
):
    """
    Retorna logs recentes em memória (últimas 500 entradas).
    Exemplos:
      GET /system/logs?source=ASANA
      GET /system/logs?source=BOT&level=ERROR&tail=50
    """
    entries = get_log_buffer()

    if source:
        entries = [e for e in entries if e["source"].upper() == source.upper()]
    if level:
        entries = [e for e in entries if e["level"].upper() == level.upper()]

    return {
        "total": len(entries),
        "logs": entries[-tail:],
    }
