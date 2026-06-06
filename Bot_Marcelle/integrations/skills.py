"""
Skills toggle por instância — leitura via banco compartilhado.
Default: skill habilitada (ausência de registro = enabled).
"""

from integrations.postgres import get_pool
from core.logger import bot_logger

# Skills que nunca podem ser desligadas (espelho do Skill::CATALOG no Rails)
ALWAYS_ON = frozenset({"chat", "media"})


async def is_skill_enabled(instance_id: str, skill_id: str) -> bool:
    """Retorna True se a skill está ativa para esta instância."""
    if skill_id in ALWAYS_ON:
        return True

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT enabled FROM bots.instance_skills WHERE instance_id = $1 AND skill_id = $2",
            instance_id, skill_id,
        )

    # Sem override → enabled por default
    if row is None:
        return True
    return bool(row["enabled"])


async def get_disabled_skills(instance_id: str) -> set[str]:
    """Conjunto de skills desabilitadas para essa instância."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT skill_id FROM bots.instance_skills WHERE instance_id = $1 AND enabled = FALSE",
            instance_id,
        )
    disabled = {r["skill_id"] for r in rows} - ALWAYS_ON
    if disabled:
        bot_logger.debug(f"[SKILLS] instance={instance_id} desabilitadas: {disabled}")
    return disabled
