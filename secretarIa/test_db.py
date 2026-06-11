import asyncio
import os
import asyncpg
from dotenv import load_dotenv

async def main():
    load_dotenv()
    db_url = os.getenv("POSTGRES_URL")
    
    print(f"Tentando conectar com a URL configurada...")
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Conexao estabelecida com sucesso!")
        
        # Verifica o banco de dados atual
        db_name = await conn.fetchval('SELECT current_database();')
        print(f"Banco de Dados atual: {db_name}")
        
        # Verifica o schema (search_path)
        search_path = await conn.fetchval('SHOW search_path;')
        print(f"Schema (Search Path) atual: {search_path}")
        
        await conn.close()
    except Exception as e:
        print(f"Falha na conexao: {e}")

if __name__ == "__main__":
    asyncio.run(main())
