"""
Handler de Custom Skills — skills criadas pelo admin sem código.

Matching:
  - Texto recebido em lowercase
  - match_whole_word=False: substring match (`'preço' in text`)
  - match_whole_word=True: regex \bkeyword\b

Templates suportam placeholders simples:
  - {{phone}}  → telefone do remetente
  - {{instance_name}} → nome da instância
"""

import re
from typing import Optional

from core.logger import bot_logger
from integrations.postgres import get_pool


def _matches(text: str, keyword: str, whole_word: bool) -> bool:
    kw = keyword.strip().lower()
    if not kw:
        return False
    if whole_word:
        return bool(re.search(rf"\b{re.escape(kw)}\b", text, flags=re.IGNORECASE))
    return kw in text.lower()


def _render_template(template: str, *, phone: str, instance_name: str) -> str:
    return (
        template
        .replace("{{phone}}", phone or "")
        .replace("{{instance_name}}", instance_name or "")
    )


async def try_custom_skill(instance_id: str, text: str, phone: str, instance_name: str) -> Optional[str]:
    """
    Tenta casar uma custom skill ativa. Retorna o template renderizado ou None.
    Se mais de uma casar, vence a com o nome alfabeticamente menor (determinístico).
    """
    if not text or not instance_id:
        return None

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, keywords, match_whole_word, response_template
            FROM bots.custom_skills
            WHERE instance_id = $1 AND enabled = TRUE
            ORDER BY lower(name)
            """,
            instance_id,
        )

    for row in rows:
        for kw in row["keywords"]:
            if _matches(text, kw, row["match_whole_word"]):
                bot_logger.info(
                    f"[CUSTOM_SKILL] match '{row['name']}' | keyword='{kw}' | instance={instance_id}"
                )
                return _render_template(
                    row["response_template"],
                    phone=phone,
                    instance_name=instance_name,
                )

    return None
