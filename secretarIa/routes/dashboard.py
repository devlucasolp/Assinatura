from fastapi import APIRouter, Body, HTTPException
from core.logger import system_logger
import os
from integrations.postgres import (
    list_instances,
    get_instance,
    upsert_instance,
    delete_instance
)
from integrations.evolution_api import (
    create_evolution_instance,
    get_evolution_qr_code,
    set_evolution_webhook,
    fetch_instances,
    get_instance_status,
    logout_instance,
    restart_instance,
    delete_instance,
    get_instance_settings,
    update_instance_settings,
    update_instance_profile
)

router = APIRouter(prefix="/api/instances", tags=["Instances"])
evolution_router = APIRouter(prefix="/api/evolution", tags=["Evolution Global"])

@evolution_router.get("/instances")
async def get_all_evolution_instances():
    """Retorna todas as instâncias existentes na Evolution API."""
    try:
        data = await fetch_instances()
        return data
    except Exception as e:
        system_logger.error(f"[EVOLUTION] Erro ao listar instâncias globais: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_all_instances():
    """Retorna todas as instâncias."""
    instances = await list_instances()
    return instances

@router.get("/{instance_id}")
async def get_instance_by_id(instance_id: str):
    """Retorna os detalhes de uma instância."""
    inst = await get_instance(instance_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instância não encontrada")
    return inst

@router.post("")
async def create_or_update_instance(data: dict = Body(...)):
    """Cria ou atualiza uma instância."""
    if "id" not in data or "name" not in data or "evolution_instance" not in data:
        raise HTTPException(status_code=400, detail="Faltam campos obrigatórios (id, name, evolution_instance)")
    
    try:
        result = await upsert_instance(data)
        system_logger.info(f"[DASHBOARD] Instância salva: {result['id']}")
        return {"status": "success", "instance": result}
    except Exception as e:
        system_logger.error(f"[DASHBOARD] Erro ao salvar instância: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{instance_id}")
async def remove_instance(instance_id: str):
    """Deleta uma instância."""
    try:
        deleted = await delete_instance(instance_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Instância não encontrada")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{instance_id}/evolution/create")
async def create_evolution(instance_id: str):
    """Cria a instância na Evolution API e seta o webhook."""
    inst = await get_instance(instance_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instância não encontrada no banco.")
    
    evo_name = inst.get("evolution_instance")
    if not evo_name:
        raise HTTPException(status_code=400, detail="Instância não tem evolution_instance configurado.")
        
    try:
        # Tenta criar a instância (se já existir, a Evolution pode retornar erro, capturamos e ignoramos)
        try:
            await create_evolution_instance(evo_name)
        except Exception as e:
            system_logger.warning(f"Instância {evo_name} já existe na Evolution ou erro ao criar: {e}")
        
        # Configurar webhook
        public_url = os.getenv("BOT_PUBLIC_URL")
        if not public_url:
            raise HTTPException(status_code=500, detail="BOT_PUBLIC_URL não configurado no .env")
            
        webhook_url = f"{public_url.rstrip('/')}/webhook/evolution/messages"
        await set_evolution_webhook(evo_name, webhook_url)
        
        return {"status": "success", "message": "Instância configurada na Evolution API."}
    except Exception as e:
        system_logger.error(f"[EVOLUTION] Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{instance_id}/evolution/qr")
async def get_evolution_qr(instance_id: str):
    """Busca o QR Code Base64 da Evolution API."""
    inst = await get_instance(instance_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instância não encontrada no banco.")
    
    evo_name = inst.get("evolution_instance")
    if not evo_name:
        raise HTTPException(status_code=400, detail="Instância não tem evolution_instance configurado.")
        
    try:
        data = await get_evolution_qr_code(evo_name)
        # Evolution retorna {"base64": "..."} ou dependendo do status {"instance": ...}
        # Retornamos tudo para o frontend processar
        return data
    except Exception as e:
        system_logger.error(f"[EVOLUTION QR] Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _get_evo_name(instance_id: str) -> str:
    inst = await get_instance(instance_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instância não encontrada no banco.")
    evo_name = inst.get("evolution_instance")
    if not evo_name:
        raise HTTPException(status_code=400, detail="Instância não tem evolution_instance configurado.")
    return evo_name

@router.get("/{instance_id}/evolution/status")
async def api_evolution_status(instance_id: str):
    evo_name = await _get_evo_name(instance_id)
    try:
        return await get_instance_status(evo_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{instance_id}/evolution/logout")
async def api_evolution_logout(instance_id: str):
    evo_name = await _get_evo_name(instance_id)
    try:
        return await logout_instance(evo_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{instance_id}/evolution/restart")
async def api_evolution_restart(instance_id: str):
    evo_name = await _get_evo_name(instance_id)
    try:
        return await restart_instance(evo_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{instance_id}/evolution")
async def api_evolution_delete(instance_id: str):
    evo_name = await _get_evo_name(instance_id)
    try:
        return await delete_instance(evo_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{instance_id}/evolution/settings")
async def api_evolution_settings_get(instance_id: str):
    evo_name = await _get_evo_name(instance_id)
    try:
        return await get_instance_settings(evo_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{instance_id}/evolution/settings")
async def api_evolution_settings_set(instance_id: str, data: dict = Body(...)):
    evo_name = await _get_evo_name(instance_id)
    try:
        return await update_instance_settings(evo_name, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{instance_id}/evolution/profile")
async def api_evolution_profile_set(instance_id: str, data: dict = Body(...)):
    evo_name = await _get_evo_name(instance_id)
    try:
        return await update_instance_profile(evo_name, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

