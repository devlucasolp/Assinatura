"""
Cria container Docker efêmero, executa código, captura resultado, mata.
Sem rede neste PR (PR 2 traz allow-list via proxy).
"""

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Literal

import docker
from docker.errors import ContainerError, ImageNotFound, APIError

from config import LIMITS, SETTINGS

log = logging.getLogger(__name__)

_client = docker.from_env()

KillReason = Literal["timeout", "oom", "manual", None]


@dataclass
class RunResult:
    stdout:          str
    stderr:          str
    exit_code:       int
    duration_ms:     int
    memory_peak_mb:  int | None
    killed:          bool
    kill_reason:     KillReason
    error:           str | None = None


def _truncate(text: bytes, max_bytes: int) -> str:
    if len(text) <= max_bytes:
        return text.decode("utf-8", errors="replace")
    head = text[:max_bytes].decode("utf-8", errors="replace")
    return head + f"\n[... truncated, {len(text) - max_bytes} bytes more]"


def run_code(
    code: str,
    *,
    instance_id: str,
    timeout_seconds: int | None = None,
    memory_mb:       int | None = None,
    cpus:            float | None = None,
) -> RunResult:
    """
    Executa código Python num container efêmero.
    Limites são clampados ao máximo definido em config.LIMITS.
    instance_id é passado via env var pro código e pro proxy de egress.
    """
    # Clamp: pedidos do caller nunca podem ser MAIS permissivos que os defaults
    timeout = min(timeout_seconds or LIMITS.timeout_seconds, LIMITS.timeout_seconds)
    mem_mb  = min(memory_mb       or LIMITS.memory_mb,       LIMITS.memory_mb)
    cpu     = min(cpus            or LIMITS.cpus,            LIMITS.cpus)

    name = f"sbx-{uuid.uuid4().hex[:12]}"
    started = time.monotonic()

    # Env vars do container: HTTP_PROXY se configurado, instance_id sempre
    env: dict[str, str] = {"SANDBOX_INSTANCE_ID": instance_id}
    if SETTINGS.egress_proxy_url:
        # Cliente HTTP do código vai usar essas vars (httpx, requests, urllib respeitam)
        env["HTTP_PROXY"]  = SETTINGS.egress_proxy_url
        env["HTTPS_PROXY"] = SETTINGS.egress_proxy_url
        env["NO_PROXY"]    = ""  # sem bypass

    try:
        container = _client.containers.create(
            image=SETTINGS.sandbox_image,
            name=name,
            command=["timeout", "--signal=KILL", f"{timeout}s", "python", "-c", code],

            # Rede: "none" no PR 1; "sandbox-net" no PR 2 (vê só o proxy)
            network_mode=SETTINGS.sandbox_network,
            environment=env,

            read_only=True,
            tmpfs={"/tmp": f"rw,size={LIMITS.tmpfs_mb}m,mode=1777"},

            # Limites de recursos
            mem_limit=f"{mem_mb}m",
            memswap_limit=f"{mem_mb}m",                  # sem swap
            nano_cpus=int(cpu * 1_000_000_000),
            pids_limit=LIMITS.pids_max,

            # Hardening
            user="sandbox",
            cap_drop=["ALL"],
            security_opt=["no-new-privileges:true"],

            # Capturar logs
            stdout=True,
            stderr=True,
            detach=True,
            auto_remove=False,                           # removemos manualmente após coletar stats
        )
    except ImageNotFound:
        return RunResult("", "", -1, 0, None, False, None,
                         error=f"Imagem '{SETTINGS.sandbox_image}' não encontrada. Build necessária.")
    except APIError as e:
        return RunResult("", "", -1, 0, None, False, None, error=f"Docker API: {e.explanation}")

    try:
        container.start()

        try:
            exit_status = container.wait(timeout=timeout + 2)  # +2s margem além do timeout interno
            exit_code = exit_status.get("StatusCode", -1)
            killed_by_oom = exit_status.get("Error") and "oom" in str(exit_status.get("Error")).lower()
        except Exception:
            # Worker estourou esperando: força kill
            try: container.kill()
            except Exception: pass
            exit_code = 137
            killed_by_oom = False

        duration_ms = int((time.monotonic() - started) * 1000)

        stdout = _truncate(container.logs(stdout=True, stderr=False), LIMITS.output_max_bytes)
        stderr = _truncate(container.logs(stdout=False, stderr=True), LIMITS.output_max_bytes)

        memory_peak_mb: int | None = None
        kill_reason: KillReason = None

        try:
            stats = container.stats(stream=False)
            peak_bytes = stats.get("memory_stats", {}).get("max_usage")
            if peak_bytes:
                memory_peak_mb = int(peak_bytes / 1_048_576)
        except Exception:
            pass

        # Classificação do kill
        # exit 124 = `timeout` GNU normal; 137 = SIGKILL (timeout --signal=KILL ou OOM)
        killed = exit_code in (124, 137)
        if killed:
            if killed_by_oom or (memory_peak_mb and memory_peak_mb >= mem_mb * 0.95):
                kill_reason = "oom"
            else:
                kill_reason = "timeout"

        return RunResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_ms=duration_ms,
            memory_peak_mb=memory_peak_mb,
            killed=killed,
            kill_reason=kill_reason,
        )

    except ContainerError as e:
        return RunResult("", str(e), e.exit_status, 0, None, False, None, error=str(e))
    except Exception as e:
        log.exception("Erro inesperado executando sandbox")
        return RunResult("", "", -1, 0, None, False, None, error=str(e))
    finally:
        try:
            container.remove(force=True)
        except Exception:
            pass
