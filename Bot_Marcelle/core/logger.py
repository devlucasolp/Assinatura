"""
Módulo de logging centralizado do projeto Assinatura - Gabi Bot
Separa visualmente logs do Bot, System e integrações externas
"""

import logging
import sys
from collections import deque
from enum import Enum


class LogSource(str, Enum):
    BOT = "BOT"
    SYSTEM = "SYSTEM"
    EVOLUTION = "EVOLUTION_API"
    GEMINI = "GEMINI"
    ASANA = "ASANA"
    POSTGRES = "POSTGRES"
    REDIS = "REDIS"
    WEBHOOK = "WEBHOOK"
    APP = "APP"


LOG_COLORS = {
    LogSource.BOT: "\033[94m",       # Azul
    LogSource.SYSTEM: "\033[92m",    # Verde
    LogSource.EVOLUTION: "\033[95m", # Magenta
    LogSource.ASANA: "\033[93m",     # Amarelo
    LogSource.POSTGRES: "\033[90m",  # Cinza
    LogSource.REDIS: "\033[91m",     # Vermelho
    LogSource.WEBHOOK: "\033[97m",   # Branco
    LogSource.APP: "\033[0m",        # Default
}
RESET = "\033[0m"


# Ring buffer in-memory — últimas 500 entradas de log
_log_buffer: deque[dict] = deque(maxlen=500)


def get_log_buffer() -> list[dict]:
    """Retorna cópia dos logs recentes em memória."""
    return list(_log_buffer)


class GabiFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        source = getattr(record, "source", LogSource.APP)
        color = LOG_COLORS.get(source, "\033[0m")
        prefix = f"{color}[{source}]{RESET}"
        record.msg = f"{prefix} {record.msg}"
        return super().format(record)


class BufferHandler(logging.Handler):
    """Handler que grava cada registro no ring buffer sem formatação ANSI."""
    def emit(self, record: logging.LogRecord) -> None:
        source = getattr(record, "source", LogSource.APP)
        _log_buffer.append({
            "time": self.formatter.formatTime(record, "%Y-%m-%d %H:%M:%S") if self.formatter else "",
            "level": record.levelname,
            "source": str(source),
            "msg": record.getMessage(),
        })


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("gabi")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = "%(asctime)s %(levelname)-8s %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Handler stdout (com cores para o terminal)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(GabiFormatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(stream_handler)

    # Handler ring buffer (sem ANSI, para o endpoint /system/logs)
    buf_handler = BufferHandler()
    buf_handler.setLevel(logging.DEBUG)
    buf_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(buf_handler)

    logger.propagate = False
    return logger


_base_logger = _build_logger()


def get_logger(source: LogSource) -> logging.LoggerAdapter:
    """Retorna um LoggerAdapter com a fonte já configurada."""
    return logging.LoggerAdapter(_base_logger, extra={"source": source})


# Loggers pré-instanciados para cada módulo
bot_logger = get_logger(LogSource.BOT)
system_logger = get_logger(LogSource.SYSTEM)
evolution_logger = get_logger(LogSource.EVOLUTION)
gemini_logger = get_logger(LogSource.GEMINI)
asana_logger = get_logger(LogSource.ASANA)
postgres_logger = get_logger(LogSource.POSTGRES)
redis_logger = get_logger(LogSource.REDIS)
webhook_logger = get_logger(LogSource.WEBHOOK)
app_logger = get_logger(LogSource.APP)
