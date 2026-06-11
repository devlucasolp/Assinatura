"""
WEBHOOK - Rota principal que recebe eventos da Evolution API (WhatsApp)

Fluxo com debounce:
  1. Recebe mensagem
  2. Auto-reply imediato (se Gabi estiver em reunião/evento)
  3. Caso contrário, enfileira no Redis + agenda processamento após 4s de silêncio
  4. Background task agrupa todas as mensagens rápidas e roteia uma única vez:
     → /ata → handler de ata de reunião (Asana + Postgres)
     → "criar tarefa" etc. → handler de tarefa genérica no Asana
     → qualquer outro → chat geral com Gemini
"""

import asyncio
from dataclasses import dataclass
from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from core.config import get_settings
from core.domain import PhoneNumber, MessageText
from core.logger import webhook_logger
from system.handlers.meeting_notify import handle_incoming_message_auto_reply
from bot.handlers.meeting_minutes import is_ata_request, handle_ata_request
from bot.handlers.asana_task import (
    is_asana_task_request, handle_asana_task_request,
    is_asana_update_request, handle_asana_update_request,
    is_asana_delete_request, handle_asana_delete_request,
    is_asana_complete_request, handle_asana_complete_request,
    is_asana_search_request,
    handle_asana_pending_response,
)
from bot.handlers.media import is_supported_media, process_media_to_text
from bot.llm.gemini_chat import process_user_message, classify_intent
from bot.handlers.asana_query import handle_asana_query
from integrations.evolution_api import send_text_message
from integrations.postgres import get_conversation_history
from integrations.redis_client import (
    DEBOUNCE_TTL,
    push_message_to_queue,
    set_debounce,
    debounce_active,
    pop_all_queued_messages,
    get_last_task,
    get_asana_pending,
    _k,
)
from core.context import current_instance, get_current_instance
from core.instance_store import get_instance_config

router = APIRouter()
settings = get_settings()

_DEBOUNCE_WAIT = DEBOUNCE_TTL + 0.5

_MEDIA_FEEDBACK = {
    "audioMessage": "🎙️ Ouvindo seu áudio...",
    "pttMessage":   "🎙️ Ouvindo seu áudio...",
    "imageMessage":  "🖼️ Lendo sua imagem...",
}

_GREETING_TRIGGERS = {"oi", "ola", "olá", "menu", "ajuda", "comandos"}


@dataclass(frozen=True)
class WebhookMessage:
    sender_phone: PhoneNumber
    text: MessageText
    is_group: bool
    from_me: bool
    is_media: bool
    raw_data: dict


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _extract_message(payload: dict) -> WebhookMessage | None:
    event = payload.get("event", "")
    if event not in ("messages.upsert", "message"):
        return None

    data = payload.get("data", {})
    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "")

    sender_phone_str = remote_jid.replace("@s.whatsapp.net", "")
    sender_phone_str = sender_phone_str.replace("@g.us", "")

    message_data = data.get("message", {})
    extended_text = message_data.get("extendedTextMessage", {})
    raw_text = (
        message_data.get("conversation")
        or extended_text.get("text")
        or ""
    ).strip()

    return WebhookMessage(
        sender_phone=PhoneNumber(sender_phone_str),
        text=MessageText(raw_text),
        is_group=remote_jid.endswith("@g.us"),
        from_me=key.get("fromMe", False),
        is_media=is_supported_media(data),
        raw_data=data,
    )


# ---------------------------------------------------------------------------
# Group mention
# ---------------------------------------------------------------------------

def _is_gabi_mentioned(msg: WebhookMessage) -> bool:
    if not msg.is_group:
        return False
    raw_data = msg.raw_data
    message_data = raw_data.get("message", {})
    extended = message_data.get("extendedTextMessage", {})
    context_info = extended.get("contextInfo", {})
    mentioned_jids = context_info.get("mentionedJid", [])
    
    instance = get_current_instance()
    primary_value = instance.get("phone_primary", "")
    gabi_jid = f"{primary_value}@s.whatsapp.net"
    
    lower_text = msg.text.lower()
    text_value = msg.text.value
    primary_mention = f"@{primary_value}"
    
    return (
        gabi_jid in mentioned_jids
        or "@gabriela" in lower_text
        or "@gabi" in lower_text
        or primary_mention in text_value
    )


# ---------------------------------------------------------------------------
# Link request
# ---------------------------------------------------------------------------

def _format_task_link(task: dict) -> str:
    lines = [f"*{task['name']}*", f"Link: {task['link']}"]
    if task.get("project"):
        lines.insert(1, f"Projeto: {task['project']}")
    return "\n".join(lines)


async def _handle_link_request(phone: str) -> None:
    task = await get_last_task(phone)
    text = (
        _format_task_link(task)
        if task and task.get("link")
        else "Não tenho o link salvo. Se a tarefa foi criada, o link foi enviado na mensagem de confirmação."
    )
    instance = get_current_instance()
    await send_text_message(to=phone, text=text, evolution_instance=instance["evolution_instance"])


# ---------------------------------------------------------------------------
# Intent routing
# ---------------------------------------------------------------------------

async def _try_keyword_route(phone: str, text: str, disabled_skills: set[str]) -> bool:
    """Tenta rotear por keyword respeitando skills desabilitadas. Retorna True se um handler foi executado."""
    checks = [
        ("ata",        is_ata_request,        lambda: handle_ata_request(sender_phone=phone, raw_message=text)),
        ("asana_task", is_asana_task_request, lambda: handle_asana_task_request(sender_phone=phone, text=text)),
    ]
    for skill_id, predicate, handler in checks:
        if predicate(text) and skill_id not in disabled_skills:
            await handler()
            return True
    return False


async def _dispatch_intent(intent: str, phone: str, text: str) -> None:
    handlers = {
        "asana_task":    lambda: handle_asana_task_request(sender_phone=phone, text=text),
        "link_request":  lambda: _handle_link_request(phone),
        "ata":           lambda: handle_ata_request(sender_phone=phone, raw_message=text),
    }
    handler = handlers.get(intent)
    if handler:
        await handler()
        return
    response = await process_user_message(phone=phone, message=text)
    instance = get_current_instance()
    await send_text_message(to=phone, text=response, evolution_instance=instance["evolution_instance"])


async def _route_combined_message(phone: str, text: str) -> None:
    pending = await get_asana_pending(phone)
    if pending:
        webhook_logger.info(f"[WEBHOOK] Continuando fluxo pendente '{pending.get('step')}' para {phone}")
        await handle_asana_pending_response(sender_phone=phone, text=text, pending=pending)
        return

    instance = get_current_instance()

    # Custom skills criadas no admin têm prioridade sobre intent routing
    from bot.handlers.custom_skill import try_custom_skill
    custom_response = await try_custom_skill(
        instance_id=instance["id"],
        text=text,
        phone=phone,
        instance_name=instance.get("name", ""),
    )
    if custom_response:
        await send_text_message(to=phone, text=custom_response, evolution_instance=instance["evolution_instance"])
        return

    from integrations.skills import get_disabled_skills
    disabled = await get_disabled_skills(instance["id"])

    if await _try_keyword_route(phone, text, disabled):
        return

    history = await get_conversation_history(phone, limit=6, instance_id=instance["id"])
    intent = await classify_intent(text, history)
    if intent in disabled:
        webhook_logger.info(f"[WEBHOOK] Intent '{intent}' desabilitado para {instance['id']} → caindo para chat")
        intent = "chat"
    else:
        webhook_logger.info(f"[WEBHOOK] Intent classificado: '{intent}' para {phone}")
    await _dispatch_intent(intent, phone, text)


# ---------------------------------------------------------------------------
# Debounce / media processing
# ---------------------------------------------------------------------------

async def _process_media_and_queue(phone: str, data: dict) -> None:
    message_type = data.get("messageType", "")
    webhook_logger.info(f"[MEDIA] Iniciando processamento de {message_type} de {phone}")

    instance = get_current_instance()
    feedback = _MEDIA_FEEDBACK.get(message_type)
    if feedback:
        await send_text_message(to=phone, text=feedback, evolution_instance=instance["evolution_instance"])

    try:
        text_result = await process_media_to_text(data)
    except Exception as exc:
        webhook_logger.exception(f"[MEDIA] Erro ao processar mídia de {phone}: {exc}")
        await send_text_message(to=phone, text="Não consegui processar essa mídia. Tenta de novo ou manda como texto.", evolution_instance=instance["evolution_instance"])
        return

    if not text_result:
        webhook_logger.warning(f"[MEDIA] Resultado vazio para {message_type} de {phone}")
        await send_text_message(to=phone, text="Não consegui processar essa mídia. Tenta de novo ou manda como texto.", evolution_instance=instance["evolution_instance"])
        return

    await push_message_to_queue(phone, text_result)
    await set_debounce(phone)
    await _process_debounced(phone)


async def _process_debounced(phone: str) -> None:
    await asyncio.sleep(_DEBOUNCE_WAIT)

    if await debounce_active(phone):
        webhook_logger.debug(f"[DEBOUNCE] Janela ainda ativa para {phone} — aguardando próxima tarefa")
        return

    messages = await pop_all_queued_messages(phone)
    if not messages:
        return

    combined = "\n".join(messages)
    webhook_logger.info(f"[DEBOUNCE] Processando {len(messages)} mensagem(ns) de {phone} | preview: {combined[:80]}")

    try:
        await _route_combined_message(phone, combined)
    except Exception as exc:
        webhook_logger.exception(f"[DEBOUNCE] Falha ao processar mensagem de {phone}: {exc}")
        instance = get_current_instance()
        await send_text_message(to=phone, text="Tive um problema técnico agora. Pode repetir?", evolution_instance=instance["evolution_instance"])


# ---------------------------------------------------------------------------
# fromMe handler (Gabi falando consigo mesma)
# ---------------------------------------------------------------------------

async def _handle_self_command(msg: WebhookMessage) -> dict:
    phone_str = msg.sender_phone.value
    lower_text = msg.text.lower()
    instance = get_current_instance()
    evo_name = instance["evolution_instance"]

    if lower_text.value == "/meet":
        from system.handlers.meeting_notify import set_status_meeting
        await set_status_meeting(60)
        await send_text_message(to=phone_str, text=instance.get("msg_status_meeting_on", "Modo Reunião"), evolution_instance=evo_name)
        return {"status": "meeting_mode_on"}

    if lower_text.value == "/evento":
        from system.handlers.meeting_notify import set_status_event
        await set_status_event(60)
        await send_text_message(to=phone_str, text=instance.get("msg_status_event_on", "Modo Evento"), evolution_instance=evo_name)
        return {"status": "event_mode_on"}

    if lower_text.value in ("/fimmeet", "/fimevento"):
        from system.handlers.meeting_notify import set_status_available
        await set_status_available()
        await send_text_message(to=phone_str, text=instance.get("msg_status_off", "Modo Desligado"), evolution_instance=evo_name)
        return {"status": "mode_off"}

    if lower_text.value in _GREETING_TRIGGERS:
        webhook_logger.info(f"[WEBHOOK] Respondendo com menu para mensagem própria de {phone_str}")
        await send_text_message(to=phone_str, text=instance.get("msg_greeting", "Olá!"), evolution_instance=evo_name)
        return {"status": "menu_sent"}

    webhook_logger.debug("[WEBHOOK] Mensagem própria ignorada")
    return {"status": "ignored"}


# ---------------------------------------------------------------------------
# Inbound handler (mensagens recebidas de terceiros ou da própria Gabi)
# ---------------------------------------------------------------------------

async def _dispatch_inbound(msg: WebhookMessage, background_tasks: BackgroundTasks) -> dict:
    phone_str = msg.sender_phone.value
    instance = get_current_instance()
    from core.domain import AuthorizedPhones
    phones = AuthorizedPhones(instance.get("phone_primary"), instance.get("phone_secondary"))

    if phones.denies(msg.sender_phone):
        is_mentioned = _is_gabi_mentioned(msg)
        auto_replied = await handle_incoming_message_auto_reply(phone_str, msg.is_group, is_mentioned)
        if auto_replied:
            webhook_logger.info(f"[WEBHOOK] Auto-reply enviado para {phone_str}")
            return {"status": "auto_replied"}
        webhook_logger.debug(f"[WEBHOOK] Mensagem de terceiro {phone_str} ignorada")
        return {"status": "ignored"}

    if msg.is_media:
        background_tasks.add_task(_process_media_and_queue_with_context, phone_str, msg.raw_data, instance)
        webhook_logger.debug(f"[WEBHOOK] Mídia de {phone_str} encaminhada para processamento em background")
        return {"status": "media_processing"}

    text_str = msg.text.value
    await push_message_to_queue(phone_str, text_str)
    await set_debounce(phone_str)
    background_tasks.add_task(_process_debounced_with_context, phone_str, instance)
    webhook_logger.debug(f"[WEBHOOK] Mensagem de {phone_str} enfileirada (debounce {DEBOUNCE_TTL}s)")
    return {"status": "queued"}


async def _process_media_and_queue_with_context(phone: str, data: dict, instance: dict):
    current_instance.set(instance)
    await _process_media_and_queue(phone, data)

async def _process_debounced_with_context(phone: str, instance: dict):
    current_instance.set(instance)
    await _process_debounced(phone)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/webhook/evolution")
async def evolution_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
    except Exception:
        webhook_logger.warning("Webhook recebido com payload inválido")
        raise HTTPException(status_code=400, detail="Payload inválido")

    # Resolve a instância a partir do payload
    instance_name = payload.get("instance", "")
    if not instance_name:
        return {"status": "ignored", "reason": "no_instance_name"}
        
    instance_config = await get_instance_config(instance_name)
    if not instance_config:
        webhook_logger.warning(f"[WEBHOOK] Instância não encontrada ou inativa: {instance_name}")
        return {"status": "ignored", "reason": "instance_not_found"}
        
    # Seta o contexto da requisição atual
    current_instance.set(instance_config)

    event = payload.get("event", "")
    webhook_logger.info(f"[WEBHOOK] Evento recebido: {event} | instance: {instance_config['name']}")

    msg = _extract_message(payload)
    if msg is None:
        webhook_logger.debug(f"[WEBHOOK] Evento '{event}' ignorado")
        return {"status": "ignored"}

    if not msg.text and not msg.is_media:
        webhook_logger.debug(f"[WEBHOOK] Mensagem sem conteúdo de {msg.sender_phone} - ignorando")
        return {"status": "ignored"}

    raw_data = msg.raw_data
    message_type = raw_data.get("messageType", "")
    text_value = msg.text.value
    preview = text_value[:60]
    webhook_logger.info(
        f"[WEBHOOK] Mensagem de {msg.sender_phone} | "
        f"tipo: {'mídia (' + message_type + ')' if msg.is_media else 'texto'}"
        + (f" | preview: {preview}" if msg.text else "")
    )

    from core.domain import AuthorizedPhones
    phones = AuthorizedPhones(instance_config.get("phone_primary"), instance_config.get("phone_secondary"))

    if msg.from_me:
        # Verifica se o ID da mensagem existe no Redis (enviada pela API do bot)
        message_id = msg.raw_data.get("key", {}).get("id")
        if message_id:
            from integrations.redis_client import get_key
            if await get_key(_k(instance_config["id"], f"sent_msg:{message_id}")):
                webhook_logger.debug(f"[WEBHOOK] Echo de saída do bot ignorado para {msg.sender_phone} (messageId: {message_id})")
                return {"status": "ignored"}

        if phones.denies(msg.sender_phone):
            webhook_logger.debug(f"[WEBHOOK] Echo de saída ignorado para {msg.sender_phone}")
            return {"status": "ignored"}

        res = await _handle_self_command(msg)
        if res.get("status") == "ignored":
            webhook_logger.info(f"[WEBHOOK] Processando mensagem própria da Gabi como inbound de {msg.sender_phone}")
            return await _dispatch_inbound(msg, background_tasks)
        return res

    return await _dispatch_inbound(msg, background_tasks)

