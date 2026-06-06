# Sandbox Worker

FastAPI service que executa código Python em containers Docker efêmeros.

**PR 1 — base sem rede.** PR 2 traz proxy HTTP com allow-list por instância.

## Arquitetura

```
Bot Python ────POST /exec────▶ Sandbox Worker ────docker run──▶ Container efêmero
                                       │                              (network=none)
                                       ▼
                                bots.sandbox_runs (Postgres)
```

## Setup local (Linux Ubuntu)

```bash
cp .env.example .env
# preenche BOT_SERVICE_KEY (copia do Rails) e DATABASE_URL

# 1. Build da imagem da sandbox
docker build -t tzolkin/sandbox-py:v1 ./image

# 2. Sobe o worker
docker compose up -d

# 3. Confere
curl http://localhost:8001/health
```

## Teste manual

```bash
curl -X POST http://localhost:8001/exec \
  -H "Content-Type: application/json" \
  -H "X-Bot-Service-Key: $BOT_SERVICE_KEY" \
  -d '{
    "code": "import pandas as pd; print(pd.DataFrame({\"a\":[1,2,3]}).sum())",
    "instance_id": "gabi-prod",
    "origin": "test"
  }'
```

Resposta esperada:
```json
{
  "stdout": "a    6\ndtype: int64\n",
  "stderr": "",
  "exit_code": 0,
  "duration_ms": 312,
  "memory_peak_mb": 87,
  "killed": false,
  "kill_reason": null,
  "error": null
}
```

## Limites padrão (em `config.py`)

| Limite | Default | Como caller restringe mais | Não pode aumentar |
|---|---|---|---|
| Timeout | 15s | `timeout_seconds: 5` | nunca passa de 15s |
| RAM | 512 MB | `memory_mb: 128` | nunca passa de 512 MB |
| CPU | 0.5 vCPU | `cpus: 0.25` | nunca passa de 0.5 |
| Processos | 64 | — | fixo |
| Disco (tmpfs) | 100 MB | — | fixo |
| Output stdout | 1 MB | — | trunca o excesso |

## Hardening aplicado (PR 1)

| Mitigação | Como |
|---|---|
| Sem rede | `network_mode=none` |
| FS read-only | `read_only=True` + tmpfs em `/tmp` |
| Sem root | `user=sandbox` (uid não-zero) |
| Sem capabilities | `cap_drop=ALL` |
| Sem escalada | `no-new-privileges:true` |
| Sem swap | `memswap_limit=mem_limit` |
| Sem fork bomb | `pids_limit=64` |
| Sem pip em runtime | `pip uninstall` no Dockerfile |

## O que **falta** (vem nos próximos PRs)

- [ ] PR 2: proxy HTTP com allow-list dinâmica por instância
- [ ] PR 2: seccomp + AppArmor profiles
- [ ] PR 2: rede `sandbox-net` isolada
- [ ] PR 3: tool `python_exec` no Gemini do bot
- [ ] PR 3: dashboard `/settings/sandbox` mostrando runs
- [ ] PR 3: suite de testes adversariais (escape attempts)
- [ ] PR 3: quota por instância
