"""
Integração com PostgreSQL - persistência de contexto e histórico
Schemas: gabi (legado), bots (multi-instância)
"""

import asyncpg
from core.config import get_settings
from core.logger import postgres_logger

settings = get_settings()
infra = settings.infra
storage = infra.storage
_POSTGRES_URL = storage.postgres_url

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        postgres_logger.info("Inicializando pool de conexões PostgreSQL")
        _pool = await asyncpg.create_pool(
            dsn=_POSTGRES_URL,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
        postgres_logger.info("Pool PostgreSQL inicializado com sucesso")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        postgres_logger.info("Fechando pool de conexões PostgreSQL")
        await _pool.close()
        _pool = None


async def setup_schema() -> None:
    """
    Cria schemas e tabelas do domínio Python (gabi.*).
    O schema bots.* é ownership do Rails — gerenciado via rails db:migrate.
    """
    pool = await get_pool()
    postgres_logger.info("Verificando/criando schemas e tabelas no PostgreSQL (gabi.*)")

    async with pool.acquire() as conn:
        await conn.execute("CREATE SCHEMA IF NOT EXISTS gabi")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS gabi.conversation_history (
                id          SERIAL PRIMARY KEY,
                instance_id TEXT        NOT NULL DEFAULT 'default',
                phone       VARCHAR(30) NOT NULL,
                role        VARCHAR(20) NOT NULL,
                content     TEXT        NOT NULL,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS gabi.meeting_minutes (
                id              SERIAL PRIMARY KEY,
                instance_id     TEXT DEFAULT 'default',
                raw_input       TEXT NOT NULL,
                processed_ata   TEXT NOT NULL,
                asana_task_gid  VARCHAR(50),
                created_at      TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS gabi.system_state (
                key        VARCHAR(100) PRIMARY KEY,
                value      TEXT NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conv_history_instance_phone
            ON gabi.conversation_history (instance_id, phone, created_at DESC)
        """)

    postgres_logger.info("Schemas e tabelas do PostgreSQL prontos (gabi.*)")


# ---------------------------------------------------------------------------
# CRUD — bots.instances
# ---------------------------------------------------------------------------

async def list_instances() -> list[dict]:
    """Lista todas as instâncias cadastradas."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM bots.instances ORDER BY created_at ASC"
        )
    result = [dict(r) for r in rows]
    postgres_logger.debug(f"Instâncias listadas: {len(result)}")
    return result


async def get_instance(instance_id: str) -> dict | None:
    """Busca instância pelo ID slug."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM bots.instances WHERE id = $1", instance_id
        )
    return dict(row) if row else None


async def get_instance_by_evolution(evolution_instance: str) -> dict | None:
    """Busca instância ativa pelo nome na Evolution API (rota crítica do webhook)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM bots.instances WHERE evolution_instance = $1 AND is_active = TRUE",
            evolution_instance,
        )
    return dict(row) if row else None


async def upsert_instance(data: dict) -> dict:
    """
    Cria ou atualiza uma instância.
    `data` deve conter pelo menos: id, name, evolution_instance.
    """
    pool = await get_pool()
    fields = [
        "id", "name", "evolution_instance",
        "phone_primary", "phone_secondary",
        "asana_access_token", "asana_workspace_gid", "asana_project_gid",
        "asana_section_gid", "asana_user_gid",
        "gemini_api_key",
        "msg_auto_reply_meeting", "msg_auto_reply_event",
        "msg_status_meeting_on", "msg_status_event_on",
        "msg_status_off", "msg_greeting",
        "is_active",
    ]
    _bool_fields = {"is_active"}
    values = [
        data.get(f, "" if f not in _bool_fields else True)
        for f in fields
    ]
    set_clause = ", ".join(
        f"{f} = ${i + 2}" for i, f in enumerate(fields[1:])
    )
    placeholders = ", ".join(f"${i + 1}" for i in range(len(fields)))
    sql = f"""
        INSERT INTO bots.instances ({', '.join(fields)}, updated_at)
        VALUES ({placeholders}, NOW())
        ON CONFLICT (id) DO UPDATE
        SET {set_clause}, updated_at = NOW()
        RETURNING *
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *values)
    result = dict(row)
    postgres_logger.info(f"Instância upserted | id: {result['id']} | name: {result['name']}")
    return result


async def update_instance_fields(instance_id: str, fields: dict) -> dict | None:
    """Atualiza apenas as colunas dadas (update parcial — usado pela config de conectores B6).

    ATENÇÃO: os nomes de coluna devem vir de uma whitelist (registro de conectores),
    nunca de input livre do usuário — são interpolados no SQL.
    """
    if not fields:
        return await get_instance(instance_id)
    keys = list(fields.keys())
    set_clause = ", ".join(f"{k} = ${i + 2}" for i, k in enumerate(keys))
    sql = f"UPDATE bots.instances SET {set_clause}, updated_at = NOW() WHERE id = $1 RETURNING *"
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, instance_id, *[fields[k] for k in keys])
    postgres_logger.info(f"[INSTANCE] Campos atualizados | id: {instance_id} | {keys}")
    return dict(row) if row else None


async def delete_instance(instance_id: str) -> bool:
    """Remove permanentemente uma instância. Retorna True se existia."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM bots.instances WHERE id = $1", instance_id
        )
    deleted = result.split()[-1] != "0"
    postgres_logger.info(f"Instância deletada | id: {instance_id} | deletado: {deleted}")
    return deleted


# ---------------------------------------------------------------------------
# Histórico de conversas (ciente de instância)
# ---------------------------------------------------------------------------

async def save_conversation_message(phone: str, role: str, content: str, instance_id: str = "default") -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO gabi.conversation_history (instance_id, phone, role, content) VALUES ($1, $2, $3, $4)",
            instance_id, phone, role, content
        )
    postgres_logger.debug(f"Mensagem salva no histórico | instance: {instance_id} | phone: {phone} | role: {role}")


async def get_conversation_history(phone: str, limit: int = 10, instance_id: str = "default") -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content FROM gabi.conversation_history
            WHERE instance_id = $1 AND phone = $2
            ORDER BY created_at DESC
            LIMIT $3
            """,
            instance_id, phone, limit
        )
    history = [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
    postgres_logger.debug(f"Histórico carregado | instance: {instance_id} | phone: {phone} | {len(history)} mensagens")
    return history


async def save_meeting_minutes(raw_input: str, processed_ata: str, asana_task_gid: str | None = None) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO gabi.meeting_minutes (raw_input, processed_ata, asana_task_gid)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            raw_input, processed_ata, asana_task_gid
        )
    record_id = row["id"]
    postgres_logger.info(f"Ata salva no PostgreSQL | id: {record_id} | asana_gid: {asana_task_gid}")
    return record_id


async def get_system_state(key: str) -> str | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT value FROM gabi.system_state WHERE key = $1", key
        )
    return row["value"] if row else None


async def set_system_state(key: str, value: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO gabi.system_state (key, value, updated_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = NOW()
            """,
            key, value
        )
    postgres_logger.debug(f"Estado do sistema atualizado | {key} = {value}")


# ---------------------------------------------------------------------------
# App settings (bots.app_settings) — configs globais gerenciáveis pelo dashboard
# ---------------------------------------------------------------------------

async def get_app_setting(key: str) -> str | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT value FROM bots.app_settings WHERE key = $1", key
        )
    return row["value"] if row else None


async def set_app_setting(key: str, value: str, is_secret: bool = False) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO bots.app_settings (key, value, is_secret, updated_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (key) DO UPDATE SET value = $2, is_secret = $3, updated_at = NOW()
            """,
            key, value, is_secret,
        )
    postgres_logger.debug(f"App setting atualizado | {key}")


async def list_app_settings(include_secrets: bool = False) -> list[dict]:
    """Lista configurações. Se include_secrets=False, mascara valores secretos."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT key, value, is_secret, updated_at FROM bots.app_settings ORDER BY key"
        )
    result = []
    for r in rows:
        entry = dict(r)
        if entry["is_secret"] and not include_secrets:
            entry["value"] = "••••••••"
        result.append(entry)
    return result


async def delete_app_setting(key: str) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM bots.app_settings WHERE key = $1", key
        )
    return result.split()[-1] != "0"


# ---------------------------------------------------------------------------
# Connector tokens (bots.connector_tokens) — OAuth tokens por conector/instância
# ---------------------------------------------------------------------------

async def get_connector_token(connector: str, instance_id: str = "__global__") -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT token_data, scope, updated_at
            FROM bots.connector_tokens
            WHERE connector = $1 AND instance_id = $2
            """,
            connector, instance_id,
        )
    return dict(row) if row else None


async def save_connector_token(
    connector: str,
    token_data: dict,
    instance_id: str = "__global__",
    scope: str | None = None,
) -> None:
    import json
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO bots.connector_tokens (connector, instance_id, token_data, scope, updated_at)
            VALUES ($1, $2, $3::jsonb, $4, NOW())
            ON CONFLICT (connector, instance_id) DO UPDATE
            SET token_data = $3::jsonb, scope = $4, updated_at = NOW()
            """,
            connector, instance_id, json.dumps(token_data), scope,
        )
    postgres_logger.info(f"Token salvo | connector: {connector} | instance: {instance_id}")


async def delete_connector_token(connector: str, instance_id: str = "__global__") -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM bots.connector_tokens WHERE connector = $1 AND instance_id = $2",
            connector, instance_id,
        )
    return result.split()[-1] != "0"


async def list_connector_tokens() -> list[dict]:
    """Lista todos os conectores sem expor o token_data completo."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT connector, instance_id, scope, updated_at
            FROM bots.connector_tokens
            ORDER BY connector, instance_id
            """
        )
    return [dict(r) for r in rows]
