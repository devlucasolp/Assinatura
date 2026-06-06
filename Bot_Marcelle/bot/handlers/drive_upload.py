"""
BOT - Handler de upload de mídia para o Google Drive.

Trigger: mensagem de imagem/documento com legenda contendo keyword de salvar.

Fluxo:
  1. Webhook detecta mídia + keyword "salva no drive" na legenda
  2. Baixa bytes via Evolution API
  3. Upload para pasta correta no Drive (Imagens / Áudios / Documentos)
  4. Retorna link de compartilhamento para o usuário
"""

import base64
from core.logger import bot_logger
from integrations.evolution_api import download_media_base64, send_text_message
from integrations.google_drive import (
    upload_file,
    make_filename,
    resolve_subfolder,
    resolve_extension,
)

DRIVE_KEYWORDS = [
    "salva no drive",
    "salvar no drive",
    "guarda no drive",
    "guardar no drive",
    "sobe pro drive",
    "subir pro drive",
    "manda pro drive",
    "salva isso",
    "guarda isso",
    "salva essa",
    "guarda essa",
    "salva esse",
    "guarda esse",
]


def is_drive_upload_request(text: str) -> bool:
    lower = text.lower().strip()
    return any(kw in lower for kw in DRIVE_KEYWORDS)


def _get_caption(data: dict) -> str:
    msg = data.get("message", {})
    return (
        msg.get("imageMessage", {}).get("caption")
        or msg.get("documentMessage", {}).get("caption")
        or msg.get("videoMessage", {}).get("caption")
        or ""
    ).strip()


async def handle_drive_upload(sender_phone: str, data: dict) -> None:
    """
    Baixa a mídia do webhook e faz upload para o Drive.
    Envia confirmação com link ou mensagem de erro para o usuário.
    """
    msg_type = data.get("messageType", "")
    caption = _get_caption(data)

    bot_logger.info(f"[DRIVE] Upload solicitado por {sender_phone} | tipo: {msg_type} | caption: {caption[:40]!r}")

    await send_text_message(to=sender_phone, text="⬆️ Enviando pro Drive...")

    try:
        b64, mime_type = await download_media_base64(data)
    except Exception as exc:
        bot_logger.error(f"[DRIVE] Falha ao baixar mídia: {exc}")
        await send_text_message(
            to=sender_phone,
            text="Não consegui baixar o arquivo. Tenta enviar de novo.",
        )
        return

    if not b64:
        await send_text_message(
            to=sender_phone,
            text="Não consegui baixar o arquivo. Tenta enviar de novo.",
        )
        return

    file_bytes = base64.b64decode(b64)
    subfolder = resolve_subfolder(mime_type)
    extension = resolve_extension(mime_type)
    filename = make_filename(caption or subfolder[:-1], extension)

    try:
        result = await upload_file(file_bytes, filename, mime_type, subfolder)
    except FileNotFoundError as exc:
        bot_logger.error(f"[DRIVE] token.json ausente: {exc}")
        await send_text_message(
            to=sender_phone,
            text="O acesso ao Drive ainda não foi configurado. Avisa o Lucas para rodar o setup.",
        )
        return
    except Exception as exc:
        bot_logger.exception(f"[DRIVE] Falha no upload: {exc}")
        await send_text_message(
            to=sender_phone,
            text="Tive um problema ao enviar pro Drive. Tenta de novo ou me passa o arquivo de outra forma.",
        )
        return

    link = result.get("webViewLink", "")
    name = result.get("name", filename)

    lines = [f"Salvo em *{subfolder}/*", f"📎 {name}"]
    if link:
        lines.append(f"Link: {link}")

    await send_text_message(to=sender_phone, text="\n".join(lines))
    bot_logger.info(f"[DRIVE] Upload concluído: '{name}' em '{subfolder}/' → {link}")
