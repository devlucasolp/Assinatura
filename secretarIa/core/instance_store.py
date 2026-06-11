"""
Gerenciamento das Instâncias na memória.
Facilita buscar a configuração de uma instância no Postgres.
"""

from integrations.postgres import get_instance, get_instance_by_evolution

async def get_instance_config(evolution_instance: str) -> dict | None:
    return await get_instance_by_evolution(evolution_instance)
