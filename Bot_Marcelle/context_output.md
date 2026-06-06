# Contexto da Sessão — Projeto Assinatura (Bot Marcelle)

> **Data:** 2026-06-05  
> **Workspace:** `d:\Códigos\Tzolkin\Projetos\Projeto Assinatura\Assinatura\Bot_Marcelle`  
> **Conversa ID:** `c39d9fd2-febb-4adb-9834-8817d8653535`

---

## 1. Projeto Atual — Estado Inicial

O projeto **Assinatura (Gabi Bot)** é um assistente executivo pessoal via WhatsApp, construído em **Python (FastAPI)**. Ele integra:

- **WhatsApp** via Evolution API (webhook de mensagens)
- **Asana** para gerenciamento de tarefas (CRUD completo, atas de reunião, busca por typeahead)
- **LLMs** (Gemini + OpenAI) para processamento de linguagem natural
- **PostgreSQL** para persistência de instâncias multi-tenant
- **Redis** para cache e estados pendentes (ex: fluxo de criação de tarefas)
- **APScheduler** para cron jobs do Asana
- **Dashboard Web** (HTML/CSS/JS vanilla) servido como arquivos estáticos pelo FastAPI

### Estrutura de Diretórios

```
Bot_Marcelle/
├── main.py                  # Entry point FastAPI + uvicorn
├── core/
│   ├── config.py            # Settings (Pydantic)
│   ├── context.py           # ContextVars para injetar instância atual
│   └── logger.py            # Loggers por módulo (asana_logger, app_logger, etc.)
├── integrations/
│   ├── asana_client.py      # Cliente Asana completo (httpx async)
│   ├── gemini_client.py     # Cliente Gemini (extração de info de tarefas)
│   ├── redis_client.py      # Redis (pendentes Asana, cache)
│   ├── postgres.py          # Pool asyncpg, CRUD de instâncias
│   └── __init__.py
├── bot/
│   ├── handlers/
│   │   ├── asana_task.py    # Handlers de criação/update/delete/complete de tarefas
│   │   ├── asana_query.py   # Handler de consultas Asana
│   │   └── meeting_minutes.py  # Handler de atas de reunião
│   └── llm/
│       └── gemini_chat.py   # Integração chat com Gemini
├── routes/
│   ├── webhook.py           # Webhook principal (Evolution API → handlers)
│   ├── dashboard.py         # API REST para CRUD de instâncias (/api/instances)
│   ├── system.py            # Rotas de sistema
│   └── teste.py             # Rotas de teste
├── dashboard/               # Frontend vanilla (servido como StaticFiles)
│   ├── index.html           # Layout: topbar + sidebar + main content
│   ├── style.css            # Design system dark theme (glassmorphism)
│   └── app.js               # Lógica do dashboard (configGroups, CRUD, tabs)
├── system/
│   └── cron_jobs.py         # APScheduler para Asana
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Arquitetura Multi-Tenant

O sistema usa `ContextVars` ([core/context.py](file:///d:/Códigos/Tzolkin/Projetos/Projeto%20Assinatura/Assinatura/Bot_Marcelle/core/context.py)) para injetar a instância atual em cada requisição. Cada instância tem suas próprias credenciais (Asana token, Gemini key, etc.) armazenadas no PostgreSQL.

---

## 2. Bug Corrigido — `_asana` não definido

### Problema
Na [linha 236 de asana_client.py](file:///d:/Códigos/Tzolkin/Projetos/Projeto%20Assinatura/Assinatura/Bot_Marcelle/integrations/asana_client.py#L236), havia uma referência a um objeto `_asana` que não existia no escopo da função `get_my_tasks()`:

```python
# ANTES (com erro)
asana_logger.debug(f"Buscando tarefas do assignee=me | workspace={_asana.workspace_gid}")
```

O erro ocorria porque a variável `workspace_gid` já estava sendo extraída corretamente do contexto na linha 230, mas o log referenciava um objeto inexistente `_asana`.

### Correção Aplicada

```diff
- asana_logger.debug(f"Buscando tarefas do assignee=me | workspace={_asana.workspace_gid}")
+ asana_logger.debug(f"Buscando tarefas do assignee=me | workspace={workspace_gid}")
```

### Validação
- Compilação com `py_compile` — sucesso
- Execução de `test_asana.py` — sucesso (sem erros de nome)

---

## 3. Refatoração do Dashboard — Seções → Páginas/Abas

### Problema
O dashboard exibia todas as 5 seções de configuração em uma única página com scroll longo, usando `IntersectionObserver` para destacar o item da sidebar.

### Solução Implementada
Convertemos para um sistema de **abas/páginas** com roteamento por hash:

#### Mudanças em [app.js](file:///d:/Códigos/Tzolkin/Projetos/Projeto%20Assinatura/Assinatura/Bot_Marcelle/dashboard/app.js):

1. **Nova função `showTabFromHash()`** — Lê o hash da URL (`#geral`, `#asana`, etc.), mostra apenas a seção correspondente e marca o nav-link como ativo.
2. **Listener `hashchange`** — Adicionado no `init()` para reagir a mudanças de hash.
3. **Substituição do `IntersectionObserver`** — Removido em favor da nova função `showTabFromHash()`.
4. **Validação inteligente ao salvar** — Se um campo obrigatório está vazio, o sistema navega automaticamente para a aba correta e foca no campo.

#### Mudanças em [style.css](file:///d:/Códigos/Tzolkin/Projetos/Projeto%20Assinatura/Assinatura/Bot_Marcelle/dashboard/style.css):

1. **`.section`** agora tem `display: none` por padrão.
2. **`.section.active`** tem `display: block` com animação `fadeInUp`.

---

## 4. Análise Comparativa — Frameworks para Escalar o Dashboard

### Opções Avaliadas

| Critério | React + Vite | Next.js (Export) | Next.js (Servidor) |
|:---|:---|:---|:---|
| Complexidade | Muito Baixa | Média | Alta |
| Performance Build | Extremamente Rápido | Rápido | Rápido |
| Curva de Aprendizado | Baixa | Média | Média |
| Deploy | Simples (FastAPI serve) | Simples (FastAPI serve) | 2 servidores (Node + Python) |
| SSR/Auth Avançado | Não | Parcial | Completo |

### Conclusão
- **Para manter deploy simples (1 servidor):** React + Vite → gera build estático, FastAPI serve.
- **Para escala corporativa (15+ pessoas, múltiplos bots):** Next.js com servidor independente.

---

## 5. Proposta de Arquitetura Corporativa — Decisão Final

### Stack Escolhida (3 Camadas)

| Camada | Tecnologia | Papel |
|:---|:---|:---|
| **Frontend** | Next.js (React + TypeScript) | UI admin rica, gráficos, configuração de bots |
| **Backend Admin** | Ruby on Rails | API REST, autenticação (Devise), RBAC, migrations, auditoria |
| **Bot Engine** | Python (FastAPI) | Webhooks WhatsApp, execução de LLMs, processamento assíncrono |

### Padrão de Arquitetura
**Decoupled Services com Event-Driven Communication (Pub/Sub)**

```
┌──────────────────────────────────────────┐
│         Frontend: Next.js (React)        │
│   UI Rica, SPA, Autenticação, Dashboard  │
└────────────────────┬─────────────────────┘
                     │ (REST API / JSON)
                     ▼
┌──────────────────────────────────────────┐
│      Backend Admin: Ruby on Rails        │
│   Devise Auth, ACL/RBAC, Migrations PG   │
└───────┬──────────────────────────┬───────┘
        │                          │
        ▼ (CRUD)                   ▼ (Pub/Sub)
┌───────────────┐           ┌──────────────┐
│  PostgreSQL   │           │  Redis Bus   │
│  (Shared DB)  │           │  (Pub/Sub)   │
└───────▲───────┘           └──────┬───────┘
        │ (Read)                   │ (Event: config_updated)
        │                          ▼
┌───────┴──────────────────────────┴───────┐
│          Bot Engine: Python (FastAPI)    │
│   Webhooks, LLM Chains, Hot Reload      │
└──────────────────────────────────────────┘
```

### Fluxo de Dados Exemplo (Alteração de Prompt)
1. **Equipe** → Edita prompt no painel Next.js
2. **Next.js** → Envia `PUT /api/bots/:id/prompt` para o Rails
3. **Rails** → Salva no PostgreSQL + publica `"instance_updated:gabi-bot"` no Redis
4. **Python** → Escuta o canal Redis, recarrega configuração do banco → Hot reload sem restart

### Benefícios Desta Arquitetura
- **Next.js:** Interface premium com TypeScript, componentes reutilizáveis, Server Actions para segurança.
- **Rails:** Convention over Configuration, ActiveRecord para velocidade de modelagem, Devise para auth enterprise-grade.
- **Python:** Mantém leveza e modularidade. Foco exclusivo em execução de IA e webhooks, sem responsabilidade de servir frontend.
- **Desacoplamento:** Cada serviço pode ser deployado, escalado e atualizado de forma independente.

### Próximos Passos Propostos
1. Criar projeto Ruby on Rails (API-only) para assumir rotas administrativas e banco
2. Criar projeto Next.js para interface do dashboard
3. Refatorar o bot Python para consumir configurações via banco compartilhado + Redis Pub/Sub
4. Remover rotas de dashboard e `StaticFiles` do `main.py` do bot
