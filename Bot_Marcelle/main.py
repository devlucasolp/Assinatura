"""
Assinatura - Gabi Bot
Ponto de entrada da aplicação FastAPI
"""

from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from core.config import get_settings
from core.logger import app_logger
from integrations.postgres import setup_schema, close_pool
from integrations.redis_client import get_redis, close_redis
from routes.webhook import router as webhook_router
from routes.system import router as system_router
from routes.dashboard import router as dashboard_router
from routes.teste import router as teste_router
from routes.auth import router as auth_router
from fastapi.staticfiles import StaticFiles
from system.cron_jobs import start_scheduler, shutdown_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização e encerramento dos recursos da aplicação."""
    app_logger.info("=" * 60)
    app_logger.info("  Assinatura - Gabi Bot iniciando...")
    app_logger.info("=" * 60)

    # Inicializa conexões (falhas não travam o boot - serviços ficam degradados)
    try:
        app_logger.info("[APP] Conectando ao Redis...")
        await get_redis()
    except Exception as e:
        app_logger.warning(f"[APP] Redis indisponível no boot: {e}")

    try:
        app_logger.info("[APP] Configurando schema PostgreSQL...")
        await setup_schema()
    except Exception as e:
        app_logger.warning(f"[APP] PostgreSQL indisponível no boot: {e}")

    try:
        app_logger.info("[APP] Iniciando Cron Jobs do Asana...")
        start_scheduler()
    except Exception as e:
        app_logger.warning(f"[APP] Falha ao iniciar APScheduler: {e}")

    app_logger.info("[APP] Boot concluído. Rotas disponíveis.")
    app_logger.info("=" * 60)

    yield

    # Encerramento
    app_logger.info("[APP] Encerrando aplicação...")
    shutdown_scheduler()
    await close_pool()
    await close_redis()
    app_logger.info("[APP] Recursos liberados. Até logo!")


app = FastAPI(
    title="Assinatura - Gabi Bot",
    description="Assistente executiva pessoal via WhatsApp",
    version="1.0.0",
    lifespan=lifespan,
)

# Rotas
app.include_router(webhook_router)
app.include_router(system_router)
app.include_router(dashboard_router)
app.include_router(teste_router)
app.include_router(auth_router)

@app.get("/health")
async def health_check():
    """Health check para o Traefik/Easypanel."""
    return {"status": "ok", "service": "gabi-bot"}

# Monta o frontend estático (deve ser a última rota)
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")


if __name__ == "__main__":
    app_config = settings.app
    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.env == "development",
        log_level="info",
    )
