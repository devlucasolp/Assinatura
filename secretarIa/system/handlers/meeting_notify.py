"""
SYSTEM - Handler de notificação automática durante reuniões/eventos
Recebe webhook de status e envia mensagem automática para quem tentar contato
"""

from core.logger import system_logger
from integrations.evolution_api import send_text_message
from integrations.redis_client import (
    get_meeting_status,
    has_auto_replied,
    mark_auto_replied,
    set_meeting_status,
)
from core.context import get_current_instance


async def handle_incoming_message_auto_reply(sender_phone: str, is_group: bool = False, is_mentioned: bool = False) -> bool:
    """
    Verifica se a Gabi está ocupada e, se sim, envia resposta automática.
    Retorna True se auto-reply foi enviado, False se não era necessário.
    """
    status = await get_meeting_status()

    if status == "available":
        return False

    if is_group and not is_mentioned:
        system_logger.debug(f"Mensagem de grupo para {sender_phone} sem menção à Gabi - ignorando auto-reply")
        return False

    already_replied = await has_auto_replied(sender_phone)
    if already_replied:
        system_logger.debug(f"Auto-reply já enviado para {sender_phone} recentemente - ignorando")
        return False

    instance = get_current_instance()
    
    _STATUS_TO_MESSAGE = {
        "meeting": instance.get("msg_auto_reply_meeting", "Estou em reunião."),
        "event": instance.get("msg_auto_reply_event", "Estou em evento."),
    }
    
    message = _STATUS_TO_MESSAGE.get(status)
    if not message:
        system_logger.warning(f"Status desconhecido '{status}' - sem auto-reply")
        return False

    system_logger.info(f"[AUTO-REPLY {status.upper()}] Enviando para {sender_phone}")
    await send_text_message(to=sender_phone, text=message, evolution_instance=instance["evolution_instance"])
    await mark_auto_replied(sender_phone)
    return True


async def set_status_meeting(duration_minutes: int | None = None) -> None:
    """Ativa modo reunião. duration_minutes: tempo estimado da reunião (opcional)."""
    system_logger.info(f"[SYSTEM] Ativando modo REUNIÃO | duração estimada: {duration_minutes} min")
    await set_meeting_status("meeting", duration_minutes)


async def set_status_event(duration_minutes: int | None = None) -> None:
    """Ativa modo evento. duration_minutes: duração estimada do evento (opcional)."""
    system_logger.info(f"[SYSTEM] Ativando modo EVENTO | duração estimada: {duration_minutes} min")
    await set_meeting_status("event", duration_minutes)


async def set_status_available() -> None:
    """Desativa qualquer modo de indisponibilidade."""
    system_logger.info("[SYSTEM] Gabi de volta - status DISPONÍVEL")
    await set_meeting_status("available")
