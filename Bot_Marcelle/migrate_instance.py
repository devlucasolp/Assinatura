"""
migrate_instance.py
-------------------
Script de migração pontual: lê o .env.prod e insere a primeira instância
na tabela bots.instances.

Uso:
    python migrate_instance.py

Execute uma vez após rodar o sistema com PostgreSQL disponível para que
o setup_schema() já tenha criado o schema e a tabela bots.instances.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import dotenv_values

# ── Carrega .env.prod ──────────────────────────────────────────────────────────
ENV_FILE = Path(__file__).parent / ".env.prod"
if not ENV_FILE.exists():
    print(f"[ERRO] Arquivo não encontrado: {ENV_FILE}")
    sys.exit(1)

env = dotenv_values(ENV_FILE)

# ── Monta o dicionário da instância ───────────────────────────────────────────
instance = {
    "id":                   "gabi-prod",
    "name":                 "Gabi — Produção",
    "evolution_instance":   env.get("EVOLUTION_INSTANCE", ""),
    "phone_primary":        env.get("GABI_PHONE", ""),
    "phone_secondary":      env.get("GABI_PHONE_2", ""),
    "asana_access_token":   env.get("ASANA_ACCESS_TOKEN", ""),
    "asana_workspace_gid":  env.get("ASANA_WORKSPACE_GID", ""),
    "asana_project_gid":    env.get("ASANA_PROJECT_GID", ""),
    "asana_section_gid":    env.get("ASANA_SECTION_GID", ""),
    "asana_user_gid":       env.get("ASANA_USER_GID", ""),
    "gemini_api_key":       env.get("GEMINI_API_KEY", ""),
    "openai_api_key":       env.get("OPENAI_API_KEY", ""),
    "openai_model":         env.get("OPENAI_MODEL", "gpt-4o"),
    # Mensagens: usa padrões do sistema; podem ser editadas pelo dashboard depois
    "msg_auto_reply_meeting":  "Oi! Estou em reunião no momento e não consigo responder agora. Assim que terminar eu te retorno. 🙏",
    "msg_auto_reply_event":    "Oi! Estou em um evento no momento e com atenção limitada. Vou te responder em breve! 🙏",
    "msg_status_meeting_on":   "✅ *Modo Reunião ativado por 1 hora.*\nQuem mandar mensagem vai receber aviso automático.",
    "msg_status_event_on":     "✅ *Modo Evento ativado por 1 hora.*\nQuem mandar mensagem vai receber aviso automático.",
    "msg_status_off":          "❌ *Auto-reply desativado.*\nBem-vinda de volta!",
    "msg_greeting":            (
        "Olá! Sou a *Fernanda*, secretária executiva da Gabriela.\n\n"
        "Posso ajudar com:\n\n"
        "📝 *Atas de reunião no Asana*\n"
        "Envie 'ata [assunto] | [transcrição ou notas]'\n\n"
        "✅ *Tarefas e reuniões no Asana*\n"
        "Ex: 'marca uma reunião com fulano amanhã às 15h'\n\n"
        "🔕 *Modo Ocupada*\n"
        "Envie '/meet' ou '/evento' para ligar a resposta automática, e '/fimmeet' para desligar."
    ),
    "is_active": True,
}


async def main():
    # Usa a POSTGRES_URL do .env.prod diretamente para não depender do .env local
    postgres_url = env.get("POSTGRES_URL", "")
    if not postgres_url:
        print("[ERRO] POSTGRES_URL não encontrada no .env.prod")
        sys.exit(1)

    import asyncpg

    print(f"[INFO] Conectando ao PostgreSQL...")
    conn = await asyncpg.connect(dsn=postgres_url)

    try:
        # Garante que o schema e a tabela existem
        await conn.execute("CREATE SCHEMA IF NOT EXISTS bots")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bots.instances (
                id                      TEXT PRIMARY KEY,
                name                    TEXT NOT NULL,
                evolution_instance       TEXT NOT NULL UNIQUE,
                phone_primary            TEXT NOT NULL DEFAULT '',
                phone_secondary          TEXT NOT NULL DEFAULT '',
                asana_access_token       TEXT NOT NULL DEFAULT '',
                asana_workspace_gid      TEXT NOT NULL DEFAULT '',
                asana_project_gid        TEXT NOT NULL DEFAULT '',
                asana_section_gid        TEXT NOT NULL DEFAULT '',
                asana_user_gid           TEXT NOT NULL DEFAULT '',
                gemini_api_key           TEXT NOT NULL DEFAULT '',
                openai_api_key           TEXT NOT NULL DEFAULT '',
                openai_model             TEXT NOT NULL DEFAULT 'gpt-4o',
                msg_auto_reply_meeting   TEXT NOT NULL DEFAULT '',
                msg_auto_reply_event     TEXT NOT NULL DEFAULT '',
                msg_status_meeting_on    TEXT NOT NULL DEFAULT '',
                msg_status_event_on      TEXT NOT NULL DEFAULT '',
                msg_status_off           TEXT NOT NULL DEFAULT '',
                msg_greeting             TEXT NOT NULL DEFAULT '',
                is_active                BOOLEAN     NOT NULL DEFAULT TRUE,
                created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        # Insere ou atualiza a instância
        row = await conn.fetchrow("""
            INSERT INTO bots.instances (
                id, name, evolution_instance,
                phone_primary, phone_secondary,
                asana_access_token, asana_workspace_gid, asana_project_gid,
                asana_section_gid, asana_user_gid,
                gemini_api_key, openai_api_key, openai_model,
                msg_auto_reply_meeting, msg_auto_reply_event,
                msg_status_meeting_on, msg_status_event_on,
                msg_status_off, msg_greeting,
                is_active, updated_at
            )
            VALUES (
                $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
                $11,$12,$13,$14,$15,$16,$17,$18,$19,$20,NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                name                  = EXCLUDED.name,
                evolution_instance    = EXCLUDED.evolution_instance,
                phone_primary         = EXCLUDED.phone_primary,
                phone_secondary       = EXCLUDED.phone_secondary,
                asana_access_token    = EXCLUDED.asana_access_token,
                asana_workspace_gid   = EXCLUDED.asana_workspace_gid,
                asana_project_gid     = EXCLUDED.asana_project_gid,
                asana_section_gid     = EXCLUDED.asana_section_gid,
                asana_user_gid        = EXCLUDED.asana_user_gid,
                gemini_api_key        = EXCLUDED.gemini_api_key,
                openai_api_key        = EXCLUDED.openai_api_key,
                openai_model          = EXCLUDED.openai_model,
                msg_auto_reply_meeting = EXCLUDED.msg_auto_reply_meeting,
                msg_auto_reply_event  = EXCLUDED.msg_auto_reply_event,
                msg_status_meeting_on = EXCLUDED.msg_status_meeting_on,
                msg_status_event_on   = EXCLUDED.msg_status_event_on,
                msg_status_off        = EXCLUDED.msg_status_off,
                msg_greeting          = EXCLUDED.msg_greeting,
                is_active             = EXCLUDED.is_active,
                updated_at            = NOW()
            RETURNING id, name, evolution_instance, phone_primary
        """,
            instance["id"], instance["name"], instance["evolution_instance"],
            instance["phone_primary"], instance["phone_secondary"],
            instance["asana_access_token"], instance["asana_workspace_gid"],
            instance["asana_project_gid"], instance["asana_section_gid"],
            instance["asana_user_gid"],
            instance["gemini_api_key"], instance["openai_api_key"], instance["openai_model"],
            instance["msg_auto_reply_meeting"], instance["msg_auto_reply_event"],
            instance["msg_status_meeting_on"], instance["msg_status_event_on"],
            instance["msg_status_off"], instance["msg_greeting"],
            instance["is_active"],
        )

        print(f"\n✅ Instância migrada com sucesso!")
        print(f"   ID:              {row['id']}")
        print(f"   Nome:            {row['name']}")
        print(f"   Instância Evol.: {row['evolution_instance']}")
        print(f"   Telefone:        {row['phone_primary']}")
        print(f"\n   Acesse o Dashboard e edite as mensagens de auto-reply se necessário.")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
