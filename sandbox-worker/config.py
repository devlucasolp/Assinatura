"""Configuração do sandbox-worker — defaults sãos, override por env."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Limits:
    """Limites padrão por execução. Caller pode pedir mais restritivo, nunca mais permissivo."""
    timeout_seconds:   int = 15
    memory_mb:         int = 512
    cpus:              float = 0.5
    pids_max:          int = 64
    output_max_bytes:  int = 1_048_576   # 1 MB por stream (stdout / stderr)
    tmpfs_mb:          int = 100
    quota_per_minute:  int = 60          # exec/min por instância (Redis)


@dataclass(frozen=True)
class Settings:
    bot_service_key:    str
    sandbox_image:      str
    postgres_url:       str
    log_runs:           bool
    sandbox_network:    str   # rede docker dos containers efêmeros (PR 2)
    egress_proxy_url:   str   # ex: http://sandbox-egress:8888 — vazio = sem rede
    redis_url:          str   # rate limit por instância (vazio = quota desabilitada)

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            bot_service_key  = os.getenv("BOT_SERVICE_KEY", ""),
            sandbox_image    = os.getenv("SANDBOX_IMAGE", "tzolkin/sandbox-py:v1"),
            postgres_url     = os.getenv("DATABASE_URL", ""),
            log_runs         = os.getenv("LOG_RUNS", "true").lower() == "true",
            sandbox_network  = os.getenv("SANDBOX_NETWORK", "none"),
            egress_proxy_url = os.getenv("EGRESS_PROXY_URL", ""),
            redis_url        = os.getenv("REDIS_URL", ""),
        )


LIMITS = Limits()
SETTINGS = Settings.load()
