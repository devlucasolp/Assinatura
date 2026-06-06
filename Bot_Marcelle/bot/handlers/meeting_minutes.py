"""
BOT - Handler de processamento de atas de reunião
Fluxo: Usuário envia transcrição via WPP → ChatGPT processa → Sobe pro Asana (seção: Reuniões Mensais)

Formatos aceitos:
  /ata [Assunto] | [transcrição]
  Exemplo: /ata Reunião ABPlast | Hoje discutimos...
"""

from core.logger import bot_logger
from integrations.gemini_client import process_meeting_minutes
from integrations.asana_client import create_meeting_minutes_task
from integrations.postgres import save_meeting_minutes
from integrations.evolution_api import send_text_message
from integrations.redis_client import save_asana_pending

ATA_TRIGGER_WORDS = ["/ata", "processar ata", "subir ata"]


def is_ata_request(text: str) -> bool:
    lower = text.lower().strip()
    return any(lower.startswith(trigger) for trigger in ATA_TRIGGER_WORDS)


def parse_ata_message(text: str) -> tuple[str, str]:
    """
    Extrai o assunto e o conteúdo bruto da mensagem.
    Formato esperado: /ata [Assunto] | [conteúdo]
    Se não tiver separador |, assunto = "Reunião" e tudo é conteúdo.

    Retorna: (assunto, conteúdo_bruto)
    """
    # Remove o trigger
    lower = text.lower()
    for trigger in ATA_TRIGGER_WORDS:
        if lower.startswith(trigger):
            rest = text[len(trigger):].strip()
            break
    else:
        rest = text.strip()

    # Separa assunto do conteúdo pelo pipe |
    if "|" in rest:
        parts = rest.split("|", 1)
        subject = parts[0].strip()
        content = parts[1].strip()
    else:
        subject = "Reunião"
        content = rest

    return subject, content


async def handle_ata_request(sender_phone: str, raw_message: str) -> None:
    """
    Processa solicitação de ata recebida via WhatsApp.
    1. Extrai assunto e conteúdo bruto
    2. Processa com ChatGPT no formato do projeto (Objetivo/Resumo/Próximos passos)
    3. Sobe pro Asana (seção Reuniões Mensais, nome: "DD/MM Assunto: [tema]")
    4. Salva no PostgreSQL
    5. Confirma para o usuário
    """
    bot_logger.info(f"[BOT] Solicitação de ata recebida de {sender_phone}")

    subject, raw_content = parse_ata_message(raw_message)

    if len(raw_content) < 30:
        bot_logger.warning(f"[BOT] Conteúdo da ata muito curto ({len(raw_content)} chars)")
        await send_text_message(
            to=sender_phone,
            text=(
                "Para processar a ata, envie assim:\n\n"
                "/ata [Assunto] | [transcrição ou notas da reunião]\n\n"
                "Exemplo:\n"
                "/ata Reunião ABPlast | Hoje discutimos os próximos passos da parceria..."
            ),
        )
        return

    bot_logger.info(f"[BOT] Assunto: '{subject}' | conteúdo: {len(raw_content)} chars")

    confirmed = False
    try:
        await send_text_message(
            to=sender_phone,
            text=f"Processando ata: *{subject}*...",
        )
        confirmed = True

        structured_ata = await process_meeting_minutes(raw_content)

        asana_result = await create_meeting_minutes_task(
            ata_content=structured_ata,
            meeting_subject=subject,
        )
        asana_task_gid = asana_result.get("data", {}).get("gid")

        await save_meeting_minutes(
            raw_input=raw_content,
            processed_ata=structured_ata,
            asana_task_gid=asana_task_gid,
        )

        asana_link = (
            f"https://app.asana.com/0/{asana_task_gid}"
            if asana_task_gid
            else None
        )
        bot_logger.info(f"[BOT] Ata processada | asana_gid: {asana_task_gid}")

        lines = [f"Ata registrada!\n\n*{subject}*"]
        if asana_link:
            lines.append(f"Link: {asana_link}")
        lines.append(f"---\n\n{structured_ata}")
        lines.append("\nPosso salvar essa ata também no seu Google Drive? (Responda 'sim' ou 'não')")

        await send_text_message(to=sender_phone, text="\n".join(lines))
        
        await save_asana_pending(sender_phone, {
            "step": "confirm_ata_drive",
            "subject": subject,
            "ata_content": structured_ata
        })

    except Exception as exc:
        bot_logger.exception(f"[BOT] Falha ao processar ata: {exc}")
        if confirmed:
            await send_text_message(
                to=sender_phone,
                text="Tive um problema ao processar a ata. Tenta enviar de novo.",
            )

async def handle_ata_drive_upload(sender_phone: str, text: str, pending: dict) -> None:
    from bot.handlers.asana_task import _is_affirmative, _is_negative
    from integrations.redis_client import clear_asana_pending
    from integrations.google_drive import upload_file, make_filename
    
    lower = text.lower().strip()
    
    if _is_affirmative(lower):
        await clear_asana_pending(sender_phone)
        await send_text_message(to=sender_phone, text="⬆️ Salvando ata no Drive...")
        
        subject = pending.get("subject", "Reunião")
        content = pending.get("ata_content", "")
        
        file_bytes = content.encode("utf-8")
        filename = make_filename(subject, "txt")
        
        try:
            result = await upload_file(file_bytes, filename, "text/plain", "Atas")
            link = result.get("webViewLink", "")
            name = result.get("name", filename)
            
            lines = [f"Salvo na pasta *Atas/*", f"📎 {name}"]
            if link:
                lines.append(f"Link: {link}")
                
            await send_text_message(to=sender_phone, text="\n".join(lines))
        except FileNotFoundError:
            await send_text_message(
                to=sender_phone,
                text="O acesso ao Drive ainda não foi configurado. Pede pro pessoal de tech rodar o script de setup."
            )
        except Exception as exc:
            bot_logger.exception(f"[DRIVE] Falha no upload da ata: {exc}")
            await send_text_message(
                to=sender_phone,
                text="Tive um problema ao enviar pro Drive."
            )
    elif _is_negative(lower):
        await clear_asana_pending(sender_phone)
        await send_text_message(to=sender_phone, text="Ok, a ata não foi salva no Drive.")
    else:
        await send_text_message(to=sender_phone, text="Posso salvar essa ata no seu Google Drive? (responda 'sim' ou 'não')")
