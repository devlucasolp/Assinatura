# Deploy no EasyPanel — Secretaria.ai

Guia para subir a stack nova (admin-api, dashboard-admin, Bot_Marcelle, sandbox) sem afetar o `Bot_Gabi` em produção.

## Pré-requisitos

- [V ] Bot_Gabi continua rodando (não mexer)
- [V ] Instância Evolution dedicada de teste (ex: `secretaria_test`) com número WhatsApp separado
- [V ] Repo Git criado e acessível (ver Etapa 0)
- [V ] SSH no servidor (pra build manual de 1 imagem)
- [V ] Postgres e Redis já existem (em projeto **separado** — mesma string que Bot_Gabi usa hoje)

> **Topologia:** Postgres e Redis rodam em outra rede (open source, projeto separado). Bot_Gabi e os novos apps ficam todos no projeto **`assinatura`** e acessam Postgres/Redis pelos **endpoints externos** (mesma URL que Bot_Gabi já tem no `.env`).

---

## Ordem do deploy

```
0. Criar/push repo no GitHub   ← bloqueia o resto
1. admin-api (Rails)           ← gera BOT_SERVICE_KEY no boot
2. dashboard-admin (Next.js)   ← depende de admin-api
3. Build manual via SSH        ← imagem tzolkin/sandbox-py:v1
4. sandbox (Compose)           ← worker + egress
5. bot-marcelle (Python)       ← depende de admin-api + sandbox
6. Configurar instância no dashboard
```

---

## Etapa 0 — Criar repo no GitHub

Se ainda não tem, faz no GitHub:

1. Acessa `github.com/new`
2. Nome: `assinatura-secretaria-ai` (ou o que preferir)
3. **Private** (recomendado pra MVP)
4. **Não** inicializa com README/gitignore (já temos)
5. Cria

No terminal:

```bash
cd "D:\Códigos\Tzolkin\Projetos\Projeto Assinatura\Assinatura"
git remote add origin git@github.com:SEU-USER/assinatura-secretaria-ai.git
# ou via HTTPS:
# git remote add origin https://github.com/SEU-USER/assinatura-secretaria-ai.git
git branch -M main
git push -u origin main
```

> **Repo privado + EasyPanel:** vai precisar conectar GitHub à conta EasyPanel (Settings → Git Providers → GitHub) **e** dar acesso ao repo. EasyPanel mostra um botão "Install GitHub App" — clica e seleciona o repo.

---

## Passo 1 — admin-api (Rails)

**EasyPanel: + Service → App**

| Campo | Valor |
|---|---|
| Name | `admin-api` |
| Source | GitHub (seu repo) |
| Branch | `main` |
| Build Path | `Assinatura/admin-api` |
| Build Method | **Dockerfile** |
| Internal Port | `3000` |
| Domain | (opcional, internal-only basta) |

**Env Vars:**

```env
RAILS_ENV=production

# Postgres está em outro projeto — usa o endpoint EXTERNO (mesma URL que Bot_Gabi)
DATABASE_URL=postgres://postgres:SENHA@easypanel.landcriativa.com:9000/assinatura_bot?sslmode=disable

# Segredo do JWT — TEM QUE SER IDÊNTICO no dashboard-admin (passo 2)
JWT_SECRET=COLE-UMA-STRING-ALEATORIA-LONGA-AQUI

# CORS: domínio do dashboard (separado por vírgula se mais de um)
CORS_ORIGINS=https://admin.seudominio.com

# Master key do Rails — sem newline no final
RAILS_MASTER_KEY=COLE-CONTEUDO-DO-master.key
```

**Pegar `master.key` sem `\r\n`:**
```powershell
(Get-Content "Assinatura\admin-api\config\master.key" -Raw).Trim()
```

**Gerar JWT_SECRET aleatório:**
```powershell
-join ((1..64) | ForEach { '{0:x}' -f (Get-Random -Maximum 16) })
```

**Deploy** → no log do primeiro boot procura:

```
╔══════════════════════════════════════════════════════╗
║  BOT_SERVICE_KEY gerada automaticamente              ║
║  Copie para o .env do Python:                        ║
║  RAILS_BOT_SERVICE_KEY=abc123def456...               ║
╚══════════════════════════════════════════════════════╝
```

**Anota a chave.** Se perder o log, recupera com:
```bash
docker exec admin-api bin/rails runner "puts BotServiceKey.value"
```

**Smoke test:**
```bash
curl https://admin-api.seudominio.com/up    # se expôs domínio
# ou:
docker exec admin-api curl http://localhost:3000/up
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

# JWT_SECRET → MESMA STRING do admin-api (passo 1). Sem isso, login entra em loop.
JWT_SECRET=MESMA-STRING-DO-ADMIN-API

# Endereços internos (mesma network do EasyPanel)
RAILS_API_URL=http://admin-api:3000
BOT_BACKEND_URL=http://bot-marcelle:8000

# OAUTH_SECRET — só usado no fluxo de conectar Google Drive. Pode deixar vazio
# por enquanto e configurar depois quando for testar Drive.
OAUTH_SECRET=

# Google OAuth (login social) — DESABILITADO neste deploy.
# Quando for habilitar, preenche estas 3 e adiciona o redirect URI no Google Console:
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
# GOOGLE_LOGIN_REDIRECT_URI=https://admin.seudominio.com/api/auth/google/callback
```

**Deploy** → acessa `https://admin.seudominio.com/login`.

> O botão "Entrar com Google" vai dar erro (sem `GOOGLE_CLIENT_ID`). **Use o formulário de e-mail/senha** abaixo:
> - E-mail: `brtzolkin@gmail.com`
> - Senha: `Tzolkin@2026`

---

## Passo 3 — Build da imagem sandbox-py (SSH no servidor)

```bash
ssh seu-servidor
cd /tmp
git clone git@github.com:SEU-USER/assinatura-secretaria-ai.git assinatura-tmp
# (ou HTTPS com PAT se SSH não estiver configurado)
cd assinatura-tmp
docker build -t tzolkin/sandbox-py:v1 Assinatura/sandbox-worker/image
docker images | grep sandbox-py     # confere
```

> A imagem fica no daemon Docker do host. EasyPanel referencia por nome no compose — não precisa registry.

---

## Passo 4 — sandbox (Compose)

### 4.1 — Confirma o nome exato da network do projeto `assinatura`

```bash
docker network ls | grep -i assinatura
```

Deve aparecer algo como `assinatura_default` ou simplesmente `assinatura`. Anota o nome exato — usa em **4.3**.

### 4.2 — Decide como o EasyPanel vai puxar o código

**Opção A** (repo privado): no servidor, clonar o repo num diretório fixo (ex: `/opt/assinatura`) e usar **path local** no compose. Mais simples.

```bash
ssh servidor
sudo mkdir -p /opt/assinatura
sudo chown $USER /opt/assinatura
git clone git@github.com:SEU-USER/assinatura-secretaria-ai.git /opt/assinatura
```

**Opção B** (repo público): usa URL Git no `context:` direto. Pula o clone manual.

### 4.3 — EasyPanel: + Service → Compose

| Campo | Valor |
|---|---|
| Name | `sandbox` |

**YAML para Opção A (recomendado, repo privado):**

```yaml
services:
  sandbox-egress:
    build:
      context: /opt/assinatura/Assinatura/sandbox-egress
    restart: unless-stopped
    environment:
      RAILS_API_URL: http://admin-api:3000
      BOT_SERVICE_KEY: COLE-AQUI-A-KEY-DO-PASSO-1
      LISTEN_PORT: "8888"
    networks:
      - app-shared
      - sandbox-net

  sandbox-worker:
    build:
      context: /opt/assinatura/Assinatura/sandbox-worker
    restart: unless-stopped
    depends_on:
      - sandbox-egress
    environment:
      BOT_SERVICE_KEY: COLE-AQUI-A-KEY-DO-PASSO-1
      SANDBOX_IMAGE: tzolkin/sandbox-py:v1
      # Mesmos endpoints externos que o Bot_Gabi usa
      DATABASE_URL: postgres://postgres:SENHA@easypanel.landcriativa.com:9000/assinatura_bot?sslmode=disable
      REDIS_URL: redis://default:SENHA@easypanel.landcriativa.com:PORTA
      SANDBOX_NETWORK: sandbox-net
      EGRESS_PROXY_URL: http://sandbox-egress:8888
      LOG_RUNS: "true"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - app-shared

networks:
  app-shared:
    external: true
    name: assinatura      # ou o nome exato descoberto em 4.1
  sandbox-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/24
```

> **Importante:** valores literais no YAML (sem `${VAR}`) pra evitar problema de interpolação no compose do EasyPanel. Se você atualizar a key, atualiza aqui também.

> **Atualizar código:** sempre que fizer `git push`, faz `git pull` em `/opt/assinatura` no servidor e clica "Redeploy" no compose do EasyPanel.

---

## Passo 5 — bot-marcelle (Python)

**EasyPanel: + Service → App**

| Campo | Valor |
|---|---|
| Name | `bot-marcelle` |
| Build Path | `Assinatura/Bot_Marcelle` |
| Build Method | **Dockerfile** |
| Internal Port | `8000` |
| Domain | `bot-marcelle.seudominio.com` (precisa ser público — Evolution vai chamar webhook) |

**Env Vars:**

```env
# Infra — MESMOS endpoints externos que Bot_Gabi
POSTGRES_URL=postgres://postgres:SENHA@easypanel.landcriativa.com:9000/assinatura_bot?sslmode=disable
REDIS_URL=redis://default:SENHA@easypanel.landcriativa.com:PORTA

# Evolution
EVOLUTION_API_URL=https://evolutionapi.landcriativa.com
EVOLUTION_API_KEY=<mesma key>
EVOLUTION_INSTANCE=secretaria_test     # ← INSTÂNCIA NOVA, não a da Gabi

# Telefone de teste (seu número, não o da Gabi)
GABI_PHONE=55XXXXXXXXXXX
GABI_PHONE_2=

# IA
GEMINI_API_KEY=...

# Asana (opcional pra teste — handlers de Asana vão dar erro se vazio, mas chat geral funciona)
ASANA_ACCESS_TOKEN=
ASANA_WORKSPACE_GID=
ASANA_PROJECT_GID=
ASANA_SECTION_GID=
ASANA_USER_GID=

# NOVAS — broker com Rails e sandbox
RAILS_API_URL=http://admin-api:3000
RAILS_BOT_SERVICE_KEY=<key do passo 1>
SANDBOX_WORKER_URL=http://sandbox-worker:8001

APP_ENV=production
```

**Deploy** → na UI da Evolution, edita o webhook da instância `secretaria_test`:
```
https://bot-marcelle.seudominio.com/webhook/evolution
```

---

## Passo 6 — Configurar instância no dashboard

1. Abre `https://admin.seudominio.com/login`
2. Loga `brtzolkin@gmail.com / Tzolkin@2026`
3. **Instâncias → Nova instância:**
   - **ID:** `secretaria-test` (slug)
   - **Nome:** `Secretaria — Teste`
   - **Telefone principal:** `55XXXXXXXXXXX` (mesmo do `GABI_PHONE` do bot)
   - **Evolution instance:** `secretaria_test` (deve ser **idêntico** ao nome cadastrado na Evolution)
   - **Gemini API Key:** mesma do `.env`
   - **Modelo OpenAI:** `gpt-4o` (default)
4. Salva
5. **Persona** (opcional): define nome e system prompt customizados
6. **Skills:** ativa as que quiser (default: todas ativas)
7. **Automações → Hosts HTTP permitidos:** só preenche se for testar sandbox **com rede** (ex: adiciona `api.openai.com`)

---

## Smoke tests pós-deploy

```bash
ssh servidor

# 1. Cada serviço up
docker exec dashboard-admin curl -s http://admin-api:3000/up && echo OK
docker exec dashboard-admin curl -s http://bot-marcelle:8000/health && echo OK
docker exec sandbox-worker curl -s http://localhost:8001/health && echo OK

# 2. Manda "oi" pro WhatsApp de teste → bot deve responder em até 8s

# 3. Sandbox sem rede (cálculo puro)
KEY=$(docker exec admin-api bin/rails runner "puts BotServiceKey.value")
docker exec sandbox-worker curl -X POST http://localhost:8001/exec \
  -H "X-Bot-Service-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"code":"print(40+2)","instance_id":"secretaria-test","origin":"test"}'

# 4. Adversarial suite (CRÍTICO antes de virar produção)
docker exec -e BOT_SERVICE_KEY="$KEY" sandbox-worker \
  python tests/adversarial.py
# Esperado: PASS 14 / 14
```

---

## Troubleshooting

| Sintoma | Fix |
|---|---|
| Login no dashboard entra em loop (volta pra `/login`) | `JWT_SECRET` diferente entre admin-api e dashboard-admin |
| `dashboard-admin` retorna 502 em qualquer rota | `RAILS_API_URL` errado ou network compartilhada não encontrada |
| `bot-marcelle` 401 ao chamar Rails | `RAILS_BOT_SERVICE_KEY` errada |
| Sandbox timeout sempre | imagem `tzolkin/sandbox-py:v1` não está no host — refaça Passo 3 |
| Sandbox erro "Image not found" | mesmo do anterior, imagem não foi buildada no servidor |
| Allow-list não bate | Cache do proxy de 30s — espera ou restarta `sandbox-egress` |
| `bot-marcelle` não recebe webhook | Webhook não configurado na Evolution, OU URL errada, OU bot não tem domínio público |
| Botão "Entrar com Google" dá erro | Esperado neste deploy (Google OAuth desabilitado). Use email/senha |
| **Perdeu a BOT_SERVICE_KEY** | `docker exec admin-api bin/rails runner "puts BotServiceKey.value"` |
| **Atualizou código no GitHub mas EasyPanel não pegou** | Apps: clica "Deploy" no app. Sandbox compose: `cd /opt/assinatura && git pull` no servidor + clica "Redeploy" |
| **Postgres pede usuário/senha** | Confere a URL externa no `.env` do Bot_Gabi e copia exatamente |
| **`assinatura` network não encontrada** | Roda `docker network ls \| grep -i assinatura` e usa o nome exato no compose. Pode ser `assinatura`, `assinatura_default` ou outro |
| **Sandbox containers não falam com sandbox-egress** | Containers efêmeros são criados pelo worker na `sandbox-net` — confere que o `SANDBOX_NETWORK=sandbox-net` está nas env vars do worker |
