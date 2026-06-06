from fastapi import APIRouter, Body, HTTPException
from core.logger import system_logger
from integrations.postgres import (
    list_instances,
    get_instance,
    upsert_instance,
    delete_instance
)

router = APIRouter(prefix="/api/instances", tags=["Instances"])

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
