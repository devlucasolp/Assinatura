import json
from fastapi import APIRouter, Request, BackgroundTasks
from core.logger import system_logger
from integrations.postgres import get_pool
from integrations.sandbox import execute_python

router = APIRouter(prefix="/api/webhooks", tags=["Custom Webhooks"])

async def _run_webhook(instance_id: str, slug: str, code: str, payload: str):
    system_logger.info(f"[WEBHOOK] Rodando webhook {slug} para {instance_id}")
    # Injetamos o JSON do webhook diretamente no código python rodando na sandbox
    injected_code = f"import json\nWEBHOOK_PAYLOAD = json.loads({repr(payload)})\n" + code
    res = await execute_python(code=injected_code, instance_id=instance_id, origin="admin")
    if not res.success:
        system_logger.error(f"[WEBHOOK] Falha ao rodar {slug}: {res.to_llm_message()}")
    else:
        system_logger.info(f"[WEBHOOK] Sucesso {slug}: {res.stdout.strip()}")

@router.post("/{instance_id}/{slug}")
async def handle_webhook(instance_id: str, slug: str, request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.body()
        payload = body.decode('utf-8')
        if not payload.strip():
            payload = "{}"
    except Exception:
        payload = "{}"
        
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT code FROM bots.webhooks WHERE instance_id = $1 AND slug = $2 AND enabled = TRUE",
            instance_id, slug
        )
        
    if not row:
        system_logger.warning(f"[WEBHOOK] Webhook não encontrado ou desativado: {instance_id}/{slug}")
        return {"status": "ignored", "reason": "Not found or disabled"}
        
    background_tasks.add_task(_run_webhook, instance_id, slug, row["code"], payload)
    return {"status": "ok", "message": "Webhook recebido e enfileirado para execução."}
