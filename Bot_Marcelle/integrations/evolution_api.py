"""
Integração com Evolution API - envio e recebimento de mensagens WhatsApp
"""

import httpx
from core.config import get_settings
from core.logger import evolution_logger

settings = get_settings()
infra = settings.infra
evolution = infra.evolution
raw_url = evolution.url
BASE_URL = raw_url.rstrip("/")
HEADERS = {
    "apikey": evolution.key,
    "Content-Type": "application/json",
}


async def send_text_message(to: str, text: str, evolution_instance: str, instance_id: str = "default") -> dict:
    """
    Envia mensagem de texto para um número via Evolution API.
    `to` deve estar no formato internacional sem + (ex: 5511999999999)
    """
    url = f"{BASE_URL}/message/sendText/{evolution_instance}"
    payload = {
        "number": to,
        "text": text,
    }
    evolution_logger.info(f"Enviando mensagem para {to} | preview: {text[:60]}...")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        message_data = data.get("key", {})
        message_id = message_data.get("id", "N/A")
        evolution_logger.info(f"Mensagem enviada com sucesso para {to} | messageId: {message_id}")
        
        if message_id != "N/A":
            try:
                from integrations.redis_client import set_key, _k
                # Precisamos usar o instance_id para salvar o echo-filter corretamente no Redis
                await set_key(_k(instance_id, f"sent_msg:{message_id}"), "1", expire_seconds=300)
            except Exception as e:
                evolution_logger.warning(f"Erro ao salvar messageId {message_id} no Redis: {e}")
                
        return data


async def download_media_base64(message_data: dict, evolution_instance: str) -> tuple[str, str]:
    """
    Baixa a mídia de uma mensagem via Evolution API.
    message_data: o objeto 'data' completo do webhook (inclui key + message).
    Retorna (base64_string, mimetype).
    """
    url = f"{BASE_URL}/chat/getBase64FromMediaMessage/{evolution_instance}"
    evolution_logger.debug("Baixando mídia via Evolution API")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            json={"message": message_data, "convertToMp4": False},
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()
    b64 = data.get("base64", "")
    mimetype = data.get("mimetype", "application/octet-stream")
    evolution_logger.debug(f"Mídia baixada | mimetype: {mimetype} | tamanho b64: {len(b64)}")
    return b64, mimetype


async def get_instance_status(evolution_instance: str) -> dict:
    """Verifica status da instância do Evolution API."""
    url = f"{BASE_URL}/instance/connectionState/{evolution_instance}"
    evolution_logger.debug("Verificando status da instância Evolution API")
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        instance_data = data.get("instance", {})
        state = instance_data.get("state", "unknown")
        evolution_logger.info(f"Status da instância Evolution API: {state}")
        return data
