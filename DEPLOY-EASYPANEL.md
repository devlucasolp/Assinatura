# Deploy no EasyPanel — Secretaria.ai

Guia para subir a stack nova (admin-api, dashboard-admin, Bot_Marcelle, sandbox) sem afetar o `Bot_Gabi` em produção.

## Pré-requisitos

- [ ] Bot_Gabi continua rodando (não mexer)
- [ ] Instância Evolution dedicada de teste (ex: `secretaria_test`) com número WhatsApp separado
- [ ] Repo Git acessível ao EasyPanel
- [ ] SSH no servidor (pra build manual de 1 imagem)

---

## Ordem do deploy

```
1. admin-api (Rails)         ← gera BOT_SERVICE_KEY no boot
2. dashboard-admin (Next.js) ← depende de admin-api
3. Build manual via SSH      ← imagem tzolkin/sandbox-py:v1
4. sandbox (Compose)         ← worker + egress
5. bot-marcelle (Python)     ← depende de admin-api + sandbox
```

---

## Passo 1 — admin-api (Rails)

**EasyPanel: + Service → App**

| Campo | Valor |
|---|---|
| Name | `admin-api` |
| Source | GitHub (seu repo) |
| Branch | `main` (ou a atual) |
| Build Path | `Assinatura/admin-api` |
| Build Method | **Dockerfile** |
| Internal Port | `3000` |
| Domain | `admin-api.seudominio.com` (ou só "Internal") |

**Env Vars:**

```env
RAILS_ENV=production
DATABASE_URL=postgres://postgres:SENHA@HOST:5432/assinatura_bot?sslmode=disable
JWT_SECRET=COLE-UMA-STRING-ALEATORIA-LONGA-AQUI
CORS_ORIGINS=https://admin.seudominio.com
RAILS_MASTER_KEY=COLE-O-CONTEUDO-DE-admin-api/config/master.key
```

**`master.key`:**
```powershell
Get-Content "Assinatura\admin-api\config\master.key"
```

**Deploy** → no log do primeiro boot procura:

```
╔══════════════════════════════════════════════════════╗
║  BOT_SERVICE_KEY gerada automaticamente              ║
║  Copie para o .env do Python:                        ║
║  RAILS_BOT_SERVICE_KEY=abc123def456...               ║
╚══════════════════════════════════════════════════════╝
```

**Anota essa chave** — usa nos próximos serviços.

**Smoke test:**
```bash
curl https://admin-api.seudominio.com/up
# 200 OK
```

---

## Passo 2 — dashboard-admin (Next.js)

**EasyPanel: + Service → App**

| Campo | Valor |
|---|---|
| Name | `dashboard-admin` |
| Build Path | `Assinatura/Bot_Marcelle/dashboard-admin` |
| Build Method | **Dockerfile** |
| Internal Port | `3000` |
| Domain | `admin.seudominio.com` |

**Env Vars:**

```env
NODE_ENV=production
RAILS_API_URL=http://admin-api:3000
BOT_BACKEND_URL=http://bot-marcelle:8000
OAUTH_SECRET=COLE-UMA-STRING-ALEATORIA
```

**Deploy** → acessa `https://admin.seudominio.com/login` e loga com `brtzolkin@gmail.com / Tzolkin@2026`.

---

## Passo 3 — Build da imagem sandbox-py (SSH no servidor)

```bash
ssh seu-servidor
cd /tmp
git clone <SEU-REPO> assinatura-tmp
cd assinatura-tmp
docker build -t tzolkin/sandbox-py:v1 Assinatura/sandbox-worker/image
docker images | grep sandbox-py     # confere
```

> O EasyPanel referencia essa imagem por nome — não precisa subir pra registry.

---

## Passo 4 — sandbox (Compose)

**EasyPanel: + Service → Compose**

| Campo | Valor |
|---|---|
| Name | `sandbox` |

**YAML** (substitui `SEU-USER/SEU-REPO` e `NOME-DA-NETWORK`):

```yaml
services:
  sandbox-egress:
    build:
      context: https://github.com/SEU-USER/SEU-REPO.git#main
      dockerfile: Assinatura/sandbox-egress/Dockerfile
    restart: unless-stopped
    environment:
      RAILS_API_URL: http://admin-api:3000
      BOT_SERVICE_KEY: ${BOT_SERVICE_KEY}
      LISTEN_PORT: "8888"
    networks:
      - default
      - sandbox-net

  sandbox-worker:
    build:
      context: https://github.com/SEU-USER/SEU-REPO.git#main
      dockerfile: Assinatura/sandbox-worker/Dockerfile
    restart: unless-stopped
    depends_on:
      - sandbox-egress
    environment:
      BOT_SERVICE_KEY: ${BOT_SERVICE_KEY}
      SANDBOX_IMAGE: tzolkin/sandbox-py:v1
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SANDBOX_NETWORK: sandbox-net
      EGRESS_PROXY_URL: http://sandbox-egress:8888
      LOG_RUNS: "true"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - default

networks:
  default:
    external: true
    name: NOME-DA-NETWORK   # descobre com: docker network ls | grep <projeto>
  sandbox-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/24
```

**Env Vars:**
```env
BOT_SERVICE_KEY=<a key do passo 1>
DATABASE_URL=<mesma do admin-api>
REDIS_URL=<mesma do Bot_Gabi>
```

---

## Passo 5 — bot-marcelle (Python)

**EasyPanel: + Service → App**

| Campo | Valor |
|---|---|
| Name | `bot-marcelle` |
| Build Path | `Assinatura/Bot_Marcelle` |
| Build Method | **Dockerfile** |
| Internal Port | `8000` |
| Domain | `bot-marcelle.seudominio.com` (ou só interno — Evolution chama via interno) |

**Env Vars** (copia do `Bot_Gabi` e adiciona as novas):

```env
# Infra (mesma do Bot_Gabi)
POSTGRES_URL=postgres://...
REDIS_URL=redis://...
EVOLUTION_API_URL=https://evolutionapi.landcriativa.com
EVOLUTION_API_KEY=<mesma>
EVOLUTION_INSTANCE=secretaria_test     # ← INSTÂNCIA NOVA, NÃO gabi_prod

# Telefone de teste (NÃO o número da Gabi)
GABI_PHONE=55XXXXXXXXXXX                # seu número de teste

# IA (mesma)
GEMINI_API_KEY=...

# Asana (deixe vazio ou use uma conta de teste)
ASANA_ACCESS_TOKEN=
ASANA_WORKSPACE_GID=
ASANA_PROJECT_GID=
ASANA_SECTION_GID=

# NOVAS — broker com Rails e sandbox
RAILS_API_URL=http://admin-api:3000
RAILS_BOT_SERVICE_KEY=<a key do passo 1>
SANDBOX_WORKER_URL=http://sandbox-worker:8001

APP_ENV=production
```

**Deploy** → no Evolution API, configura o webhook da instância `secretaria_test` para:
```
https://bot-marcelle.seudominio.com/webhook/evolution
```

---

## Passo 6 — Configurar instância no dashboard

1. Abre `https://admin.seudominio.com/login`
2. Loga `brtzolkin@gmail.com / Tzolkin@2026`
3. **Instâncias → Nova instância:**
   - ID: `secretaria-test`
   - Nome: `Secretaria — Teste`
   - Telefone principal: `55XXXXXXXXXXX` (mesmo do `GABI_PHONE`)
   - Evolution instance: `secretaria_test`
   - Gemini API Key: mesma do .env
4. **Persona:** define system prompt e nome da assistente
5. **Skills:** ativa as que quiser
6. **Automações → Hosts HTTP permitidos:** adiciona se for testar sandbox com rede

---

## Smoke tests pós-deploy

```bash
ssh servidor

# 1. Cada serviço up
docker exec dashboard-admin curl http://admin-api:3000/up
docker exec dashboard-admin curl http://bot-marcelle:8000/health
docker exec dashboard-admin curl http://sandbox-worker:8001/health

# 2. Manda "oi" pro WhatsApp de teste → bot deve responder

# 3. Sandbox isolada
docker exec sandbox-worker python -c "
import os, asyncio, httpx
async def t():
  r = await httpx.AsyncClient().post(
    'http://localhost:8001/exec',
    json={'code':'print(40+2)','instance_id':'secretaria-test','origin':'test'},
    headers={'X-Bot-Service-Key': os.environ['BOT_SERVICE_KEY']}
  )
  print(r.json())
asyncio.run(t())
"

# 4. Adversarial suite (CRÍTICO antes de produção)
docker exec sandbox-worker bash -c '
  BOT_SERVICE_KEY=$BOT_SERVICE_KEY \
  WORKER_URL=http://localhost:8001 \
  TEST_INSTANCE=adv-test \
  python tests/adversarial.py
'
# Esperado: PASS 14/14
```

---

## Troubleshooting

| Sintoma | Fix |
|---|---|
| `dashboard-admin` retorna 502 em qualquer rota | `RAILS_API_URL` errado ou network compartilhada não encontrada |
| `bot-marcelle` 401 ao chamar Rails | `RAILS_BOT_SERVICE_KEY` errada |
| Sandbox timeout sempre | imagem `tzolkin/sandbox-py:v1` não está no host — refaça Passo 3 |
| Allow-list não bate | Cache do proxy de 30s — espera ou restarta `sandbox-egress` |
| Login Google falha | Adicionar `https://admin.seudominio.com/api/auth/google/callback` em "Authorized redirect URIs" no Google Cloud Console |
