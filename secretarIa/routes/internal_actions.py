import os
from pydantic import BaseModel
from fastapi import APIRouter, Header, HTTPException
from core.logger import system_logger
from integrations.postgres import list_instances
from integrations.evolution_api import send_text_message

router = APIRouter(prefix="/api/internal", tags=["Internal"])

_BOT_KEY = os.getenv("RAILS_BOT_SERVICE_KEY", "")

class SendMessagePayload(BaseModel):
    instance_id: str
    phone: str
    text: str

@router.post("/send_message")
async def internal_send_message(
    payload: SendMessagePayload,
    x_bot_service_key: str = Header(None)
):
    if not _BOT_KEY or x_bot_service_key != _BOT_KEY:
        system_logger.warning("[INTERNAL] Tentativa de acesso não autorizada a /send_message")
        raise HTTPException(status_code=403, detail="Forbidden")
        
    # Pega a instância
    instances = await list_instances()
    inst = next((i for i in instances if i["id"] == payload.instance_id), None)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
        
    try:
        await send_text_message(
            to=payload.phone,
            text=payload.text,
            evolution_instance=inst["evolution_instance"]
        )
        system_logger.info(f"[INTERNAL] Mensagem enviada para {payload.phone} via webhook/sandbox")
        return {"status": "ok"}
    except Exception as e:
        system_logger.error(f"[INTERNAL] Falha ao enviar: {e}")
        raise HTTPException(status_code=500, detail=str(e))
