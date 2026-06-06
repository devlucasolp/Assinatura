"""
Egress proxy HTTP/HTTPS para containers de sandbox.

- Recebe requests dos containers (HTTP_PROXY=http://sandbox-egress:8888)
- Identifica instance_id pelo IP de origem (Docker resolve via mapping container→instance)
  → versão atual: instance_id vem do header X-Sandbox-Instance injetado pelo worker via env var
- Consulta allow-list no Rails (cacheada por 30s)
- Bloqueia IPs privados/metadata
- Passa o tráfego adiante se host permitido

Protocolo:
  - HTTP:  recebe request inteiro, valida Host, encaminha
  - HTTPS: recebe CONNECT host:port, valida host, abre tunnel TCP

Não faz TLS interception. Trafega bytes opacos no túnel HTTPS — sandbox conversa direto com o destino.
"""

import asyncio
import ipaddress
import logging
import os
import socket
import time
from typing import Optional

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s")
log = logging.getLogger("egress-proxy")

# Configuração
RAILS_API_URL    = os.getenv("RAILS_API_URL", "http://admin-api:3000").rstrip("/")
BOT_SERVICE_KEY  = os.getenv("BOT_SERVICE_KEY", "")
LISTEN_HOST      = os.getenv("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT      = int(os.getenv("LISTEN_PORT", "8888"))
ALLOWLIST_TTL    = int(os.getenv("ALLOWLIST_TTL_SECONDS", "30"))
INSTANCE_HEADER  = "X-Sandbox-Instance"

# Cache da allow-list por instância: { instance_id: (timestamp, set[patterns]) }
_allowlist_cache: dict[str, tuple[float, set[str]]] = {}


# ---------------------------------------------------------------------------
# Allow-list / bloqueio de IPs privados
# ---------------------------------------------------------------------------

def _is_blocked_ip(ip_str: str) -> bool:
    """Bloqueia IPs privados, loopback, link-local, multicast e metadata cloud."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # não parece IP — proxy só lida com hostnames; defensivamente bloqueia
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or str(ip) == "169.254.169.254"   # cloud metadata
    )


def _host_matches(host: str, pattern: str) -> bool:
    """Match exato ou wildcard *.dominio.com"""
    host = host.lower()
    pattern = pattern.lower()
    if pattern.startswith("*."):
        return host == pattern[2:] or host.endswith("." + pattern[2:])
    return host == pattern


async def _fetch_allowlist(instance_id: str) -> set[str]:
    """Busca allow-list no Rails. Cache de 30s pra reduzir RTT."""
    now = time.monotonic()
    cached = _allowlist_cache.get(instance_id)
    if cached and (now - cached[0]) < ALLOWLIST_TTL:
        return cached[1]

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{RAILS_API_URL}/internal/sandbox_allowlist/{instance_id}",
                headers={"X-Bot-Service-Key": BOT_SERVICE_KEY},
            )
            if r.status_code == 200:
                patterns = set(r.json().get("allow", []))
            else:
                log.warning(f"[ALLOWLIST] Rails respondeu {r.status_code} para {instance_id}")
                patterns = set()
    except Exception as e:
        log.warning(f"[ALLOWLIST] Falha ao buscar para {instance_id}: {e}")
        patterns = cached[1] if cached else set()

    _allowlist_cache[instance_id] = (now, patterns)
    return patterns


async def _is_host_allowed(host: str, instance_id: str) -> bool:
    if not instance_id:
        return False
    # 1. Bloqueia se for IP privado/metadata
    try:
        resolved = await asyncio.get_event_loop().getaddrinfo(host, None)
        for entry in resolved:
            ip_str = entry[4][0]
            if _is_blocked_ip(ip_str):
                log.warning(f"[BLOCK] {host} resolve para IP bloqueado {ip_str}")
                return False
    except socket.gaierror:
        return False

    # 2. Match contra allow-list
    patterns = await _fetch_allowlist(instance_id)
    return any(_host_matches(host, p) for p in patterns)


# ---------------------------------------------------------------------------
# Parser HTTP minimal
# ---------------------------------------------------------------------------

async def _read_headers(reader: asyncio.StreamReader, max_bytes: int = 16_384) -> Optional[bytes]:
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = await reader.read(4096)
        if not chunk:
            return None
        buf += chunk
        if len(buf) > max_bytes:
            return None
    return buf


def _parse_request_line(line: str) -> Optional[tuple[str, str, str]]:
    parts = line.strip().split(" ", 2)
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def _extract_header(headers_text: str, name: str) -> Optional[str]:
    name_low = name.lower() + ":"
    for line in headers_text.split("\r\n"):
        if line.lower().startswith(name_low):
            return line.split(":", 1)[1].strip()
    return None


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def _write_status(writer: asyncio.StreamWriter, code: int, msg: str, body: str = "") -> None:
    payload = body.encode("utf-8") if body else b""
    headers = (
        f"HTTP/1.1 {code} {msg}\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(payload)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("ascii")
    writer.write(headers + payload)
    await writer.drain()


async def _pipe(src: asyncio.StreamReader, dst: asyncio.StreamWriter) -> None:
    try:
        while True:
            data = await src.read(8192)
            if not data:
                break
            dst.write(data)
            await dst.drain()
    except (ConnectionResetError, BrokenPipeError, asyncio.IncompleteReadError):
        pass
    finally:
        try: dst.close()
        except Exception: pass


async def _handle_connect(host: str, port: int, instance_id: str, client_reader, client_writer) -> None:
    """HTTPS via CONNECT — abre tunnel TCP transparente."""
    if not await _is_host_allowed(host, instance_id):
        log.info(f"[DENY-HTTPS] {instance_id} → {host}:{port}")
        await _write_status(client_writer, 403, "Forbidden", f"Host '{host}' não está na allow-list desta instância.\n")
        client_writer.close()
        return

    try:
        upstream_reader, upstream_writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=10
        )
    except Exception as e:
        log.warning(f"[FAIL-HTTPS] {host}:{port} {e}")
        await _write_status(client_writer, 502, "Bad Gateway", str(e))
        client_writer.close()
        return

    log.info(f"[ALLOW-HTTPS] {instance_id} → {host}:{port}")
    client_writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
    await client_writer.drain()

    await asyncio.gather(
        _pipe(client_reader, upstream_writer),
        _pipe(upstream_reader, client_writer),
        return_exceptions=True,
    )


async def _handle_http(method: str, url: str, version: str, headers_text: str,
                       instance_id: str, client_reader, client_writer) -> None:
    """HTTP plain — reconstrói request e encaminha via httpx."""
    if not url.startswith("http://"):
        await _write_status(client_writer, 400, "Bad Request", "Apenas URLs absolutas http://")
        client_writer.close()
        return

    # Extrai host:port da URL
    try:
        from urllib.parse import urlsplit
        u = urlsplit(url)
        host = u.hostname or ""
        port = u.port or 80
    except Exception:
        await _write_status(client_writer, 400, "Bad Request", "URL inválida")
        client_writer.close()
        return

    if not await _is_host_allowed(host, instance_id):
        log.info(f"[DENY-HTTP] {instance_id} → {host}")
        await _write_status(client_writer, 403, "Forbidden", f"Host '{host}' não está na allow-list.\n")
        client_writer.close()
        return

    # Body (se houver)
    content_length = _extract_header(headers_text, "Content-Length")
    body = b""
    if content_length and content_length.isdigit():
        body = await client_reader.readexactly(int(content_length))

    # Limpa headers de hop-by-hop e Proxy
    skip = {"proxy-connection", "proxy-authorization", "connection", "host", INSTANCE_HEADER.lower()}
    fwd_headers = {}
    for line in headers_text.split("\r\n"):
        if ":" not in line: continue
        name, value = line.split(":", 1)
        if name.lower() not in skip:
            fwd_headers[name.strip()] = value.strip()

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            r = await client.request(method, url, headers=fwd_headers, content=body)
        log.info(f"[ALLOW-HTTP] {instance_id} {method} {host} → {r.status_code}")

        resp_headers = "".join(f"{k}: {v}\r\n" for k, v in r.headers.items() if k.lower() != "transfer-encoding")
        client_writer.write(
            f"HTTP/1.1 {r.status_code} {r.reason_phrase}\r\n".encode()
            + resp_headers.encode()
            + b"Connection: close\r\n\r\n"
            + r.content
        )
        await client_writer.drain()
    except Exception as e:
        log.warning(f"[FAIL-HTTP] {host} {e}")
        await _write_status(client_writer, 502, "Bad Gateway", str(e))
    finally:
        client_writer.close()


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    raw = await _read_headers(reader)
    if not raw:
        writer.close(); return

    try:
        headers_text = raw.split(b"\r\n\r\n")[0].decode("latin-1")
    except Exception:
        writer.close(); return

    lines = headers_text.split("\r\n")
    parsed = _parse_request_line(lines[0])
    if not parsed:
        await _write_status(writer, 400, "Bad Request", "Request line inválida")
        writer.close(); return

    method, target, version = parsed
    instance_id = _extract_header(headers_text, INSTANCE_HEADER) or ""

    if method.upper() == "CONNECT":
        # CONNECT host:port HTTP/1.1
        try:
            host, port_str = target.rsplit(":", 1)
            port = int(port_str)
        except Exception:
            await _write_status(writer, 400, "Bad Request", "CONNECT alvo inválido")
            writer.close(); return
        await _handle_connect(host, port, instance_id, reader, writer)
    else:
        await _handle_http(method, target, version, headers_text, instance_id, reader, writer)


async def main():
    server = await asyncio.start_server(handle_client, LISTEN_HOST, LISTEN_PORT)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets)
    log.info(f"Egress proxy escutando em {addrs} | Rails: {RAILS_API_URL}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
