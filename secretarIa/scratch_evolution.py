import os
import asyncio
from dotenv import load_dotenv
import httpx

load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")

async def main():
    headers = {"apikey": EVOLUTION_API_KEY}
    
    print(f"URL: {EVOLUTION_API_URL}")
    print(f"KEY: {EVOLUTION_API_KEY}")

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{EVOLUTION_API_URL}/instance/fetchInstances", headers=headers)
            print("Fetch Instances:")
            print(res.status_code)
            print(res.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
