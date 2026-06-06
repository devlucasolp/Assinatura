"""
BOT - Handler de mídia (áudio e imagem)

Fluxo:
  1. Webhook detecta messageType (audioMessage / imageMessage / pttMessage)
  2. Baixa a mídia via Evolution API (base64)
  3. Processa com Gemini:
     - Áudio  → transcrição de texto
     - Imagem → descrição + leitura de texto/conteúdo
  4. Devolve o texto processado para ser enfileirado no debounce normal

Tipos suportados:
  audioMessage  - mensagem de áudio gravada
  pttMessage    - push-to-talk (nota de voz)
  imageMessage  - imagem (com ou sem legenda)
"""

import base64
from core.logger import bot_logger
from integrations.evolution_api import download_media_base64
from integrations.gemini_client import transcribe_audio, describe_image

AUDIO_TYPES = {"audioMessage", "pttMessage"}
IMAGE_TYPES = {"imageMessage"}
SUPPORTED_MEDIA_TYPES = AUDIO_TYPES | IMAGE_TYPES


def get_message_type(data: dict) -> str:
    """Extrai o messageType do payload do webhook."""
    return data.get("messageType", "")


def is_supported_media(data: dict) -> bool:
    return get_message_type(data) in SUPPORTED_MEDIA_TYPES


def _get_image_caption(data: dict) -> str:
    """Extrai a legenda de uma imageMessage, se houver."""
    return (
        data.get("message", {})
        .get("imageMessage", {})
        .get("caption", "")
        or ""
    )


async def process_media_to_text(data: dict) -> str | None:
    """
    Baixa e processa a mídia, retornando uma representação em texto.
    Retorna None se o tipo não for suportado ou se falhar.

    data: o objeto 'data' completo do webhook (inclui key, message, messageType).
    """
    msg_type = get_message_type(data)

    if msg_type not in SUPPORTED_MEDIA_TYPES:
        return None

    bot_logger.info(f"[MEDIA] Processando mídia | tipo: {msg_type}")

    try:
        b64, mime_type = await download_media_base64(data)
    except Exception as e:
        bot_logger.error(f"[MEDIA] Falha ao baixar mídia ({msg_type}): {e}")
        return None

    if not b64:
        bot_logger.warning(f"[MEDIA] Base64 vazio para {msg_type}")
        return None

    media_bytes = base64.b64decode(b64)

    if msg_type in AUDIO_TYPES:
        try:
            transcription = await transcribe_audio(media_bytes, mime_type)
            if not transcription:
                bot_logger.warning("[MEDIA] Transcrição vazia")
                return None
            bot_logger.info(f"[MEDIA] Áudio transcrito | {len(transcription)} chars")
            return f"[Áudio transcrito]: {transcription}"
        except Exception as e:
            bot_logger.error(f"[MEDIA] Falha na transcrição: {e}")
            return None

    if msg_type in IMAGE_TYPES:
        caption = _get_image_caption(data)
        try:
            description = await describe_image(media_bytes, mime_type, caption)
            if not description:
                bot_logger.warning("[MEDIA] Descrição de imagem vazia")
                return None
            bot_logger.info(f"[MEDIA] Imagem descrita | {len(description)} chars")
            prefix = f"[Imagem enviada — legenda: \"{caption}\"]\n" if caption else "[Imagem enviada]\n"
            return prefix + description
        except Exception as e:
            bot_logger.error(f"[MEDIA] Falha na descrição da imagem: {e}")
            return None

    return None
