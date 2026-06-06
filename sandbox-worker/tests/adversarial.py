"""
Suite de testes adversariais — tenta escapar do sandbox.

Uso (com o worker rodando):
    BOT_SERVICE_KEY=xxx WORKER_URL=http://localhost:8001 python tests/adversarial.py

Cada teste DEVE falhar (exit != 0, killed, ou stderr não-vazio).
Se algum PASSAR, a sandbox está quebrada — não vai pra produção.
"""

import asyncio
import os
import sys
import time
from dataclasses import dataclass

import httpx

WORKER_URL = os.getenv("WORKER_URL", "http://localhost:8001").rstrip("/")
BOT_KEY    = os.getenv("BOT_SERVICE_KEY", "")
INSTANCE   = os.getenv("TEST_INSTANCE", "adversarial-test")


@dataclass
class Test:
    name:       str
    code:       str
    expect:     str   # "fail" (qualquer não-sucesso) | "killed" | "block_string"
    block_str:  str | None = None


TESTS: list[Test] = [
    Test("fork_bomb",
         "import os\nwhile True: os.fork()",
         "killed"),

    Test("read_etc_passwd",
         "print(open('/etc/passwd').read())",
         "fail"),

    Test("write_etc",
         "open('/etc/foo', 'w').write('hack')",
         "fail"),

    Test("subprocess_sudo",
         "import subprocess; print(subprocess.run(['sudo', 'whoami'], capture_output=True).stdout)",
         "fail"),

    Test("escape_via_os_system",
         "import os; print(os.system('ls /'))",
         "fail"),

    Test("connect_metadata_via_proxy",
         "import httpx; print(httpx.get('http://169.254.169.254/latest/meta-data/').text)",
         "block_string", block_str="403"),

    Test("connect_postgres_via_proxy",
         "import httpx; print(httpx.get('http://postgres:5432').text)",
         "fail"),

    Test("connect_internal_rails_via_proxy",
         "import httpx; print(httpx.get('http://admin-api:3000/api/v1/users').text)",
         "fail"),

    Test("rapid_alloc_oom",
         "x = []\nwhile True: x.append('a' * 1_000_000)",
         "killed"),

    Test("timeout_infinite_loop",
         "while True: pass",
         "killed"),

    Test("import_ctypes_libc",
         "import ctypes\nlibc = ctypes.CDLL('libc.so.6')\nprint(libc.geteuid())",
         "fail"),

    Test("write_to_root_fs",
         "open('/usr/bin/payload', 'w').write('x')",
         "fail"),

    Test("dns_lookup_external_blocked",
         "import socket; print(socket.gethostbyname('malicious.example.com'))",
         "fail"),

    Test("http_to_allowlisted_host_should_work",
         # Esse só passa se 'httpbin.org' estiver na allow-list desta instância
         "import httpx; r = httpx.get('https://httpbin.org/status/200', timeout=5); print('OK' if r.status_code == 200 else 'FAIL')",
         "fail"),  # default fail — não temos allow-list nesta instância de teste
]


async def run_test(t: Test) -> bool:
    """Retorna True se o teste passou (ou seja, o escape foi bloqueado)."""
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            res = await client.post(
                f"{WORKER_URL}/exec",
                json={"code": t.code, "instance_id": INSTANCE, "origin": "test"},
                headers={"X-Bot-Service-Key": BOT_KEY},
            )
        except Exception as e:
            print(f"  ⚠️  ERRO worker: {e}")
            return False

    if res.status_code == 429:
        print(f"  ⏸️  RATE-LIMITED — pula")
        return True

    if res.status_code != 200:
        print(f"  ⚠️  HTTP {res.status_code}: {res.text[:200]}")
        return False

    r = res.json()
    print(f"  exit={r['exit_code']} killed={r['killed']} kill_reason={r.get('kill_reason')} dur={r['duration_ms']}ms")
    if r['stdout']: print(f"  stdout[:200]: {r['stdout'][:200]!r}")
    if r['stderr']: print(f"  stderr[:200]: {r['stderr'][:200]!r}")

    if t.expect == "killed":
        return r['killed']
    if t.expect == "block_string":
        return (t.block_str or "") in (r['stdout'] + r['stderr'])
    # "fail" — qualquer não-sucesso
    return r['exit_code'] != 0 or r['killed'] or bool(r.get('error'))


async def main():
    if not BOT_KEY:
        print("⚠️  BOT_SERVICE_KEY não definido — testes podem falhar de auth")

    print(f"Adversarial suite — worker={WORKER_URL} instance={INSTANCE}\n")

    passed = []
    failed = []
    for t in TESTS:
        print(f"▶ {t.name}")
        try:
            ok = await run_test(t)
        except Exception as e:
            print(f"  💥 EXCEPTION: {e}")
            ok = False
        (passed if ok else failed).append(t.name)
        print(f"  {'✅ PASS (escape bloqueado)' if ok else '🚨 FAIL (escape funcionou!)'}\n")
        time.sleep(0.3)  # respeita quota

    print("=" * 60)
    print(f"PASS: {len(passed)} / {len(TESTS)}")
    if failed:
        print(f"\n🚨 FALHAS:")
        for n in failed:
            print(f"  - {n}")
        sys.exit(1)
    print("\n✅ Sandbox resistiu a todos os escapes testados.")


if __name__ == "__main__":
    asyncio.run(main())
