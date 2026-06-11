import asyncio
import asyncpg

async def main():
    sys_url = "postgres://postgres:3ad3550763e84d5864a7@easypanel.landcriativa.com:9000/postgres?sslmode=disable"
    
    print("Conectando ao banco de dados padrao 'postgres' para criar 'assinatura'...")
    try:
        sys_conn = await asyncpg.connect(sys_url)
        # Executando CREATE DATABASE (fora de bloco de transacao)
        await sys_conn.execute('CREATE DATABASE assinatura')
        print("Banco de dados 'assinatura' criado com sucesso.")
        await sys_conn.close()
    except asyncpg.exceptions.DuplicateDatabaseError:
        print("O banco de dados 'assinatura' ja existe.")
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")

    # Conectando no novo banco para criar o schema
    new_db_url = "postgres://postgres:3ad3550763e84d5864a7@easypanel.landcriativa.com:9000/assinatura?sslmode=disable"
    print("Conectando ao banco 'assinatura' para criar o schema 'assinaturaAi'...")
    try:
        conn = await asyncpg.connect(new_db_url)
        await conn.execute('CREATE SCHEMA IF NOT EXISTS "assinaturaAi"')
        print("Schema 'assinaturaAi' criado com sucesso.")
        await conn.close()
    except Exception as e:
        print(f"Erro ao criar schema: {e}")

if __name__ == "__main__":
    asyncio.run(main())
