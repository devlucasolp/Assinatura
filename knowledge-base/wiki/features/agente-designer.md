---
title: Agente Designer
type: feature
tags: [designer, gemini, nano-banana, next.js, express, prisma, canvas-editor, branding, posts]
sources: [designer/backend/src/routes/ai.ts, designer/backend/src/lib/nanoBanana.ts, designer/frontend/src/app/[marca]/fabrica/page.tsx, designer/backend/prisma/schema.prisma]
created: 2026-04-22
updated: 2026-04-22
---

# Agente Designer

## Resumo

App web de geração de designs visuais com IA, construído em Next.js (frontend) + Express (backend) + PostgreSQL via Prisma. Cada marca tem seu próprio agente configurado (guidelines, prompt, cores, fontes). O usuário descreve o que quer na "Fábrica" e o backend chama o Nano Banana (Gemini 2.0 Flash Lite) que devolve um JSON de camadas (layers); o editor visual renderiza e exporta as camadas. Base do produto já está no git (`designer/`, commit `e809a0f`, 2026-04-19).

## Detalhes

### Fluxo Principal (Fábrica → Design)

```
Usuário descreve no chat (Fábrica page)
  → POST /api/ai/:slug/generate-design
    → getBrandContext(slug)         ← BrandConfig no Postgres
    → generateDesign() [nanoBanana.ts]
      → Gemini 2.0 Flash Lite (JSON mode)
      → retorna DesignState[] (array de slides com layers)
    → prisma.post.create (status: DRAFT, content: Json)
  → frontend exibe link para galeria/editor
```

### Endpoints de IA (`/api/ai/:slug/`)

| Endpoint | Método | Descrição |
|---|---|---|
| `/:slug/chat` | POST | Chat streaming com Gemini (SSE) — usa brand context como system instruction |
| `/:slug/analyze-benchmark` | POST | Análise de referência/concorrente → insights em Markdown |
| `/:slug/generate-briefing` | POST | Gera guidelines + agentPrompt + suggestedColors (JSON) |
| `/:slug/generate-design` | POST | Gera DesignState[] via Nano Banana → salva como Post DRAFT |

### Modelos de Dados (Prisma)

| Model | Campos principais |
|---|---|
| `User` | id, email, password, name, role (ADMIN/DESIGNER) |
| `Brand` | id, slug, name, color, userId |
| `BrandConfig` | agentPrompt, primaryFonts, colors[], guidelines, logoUrl — 1:1 com Brand |
| `Reference` | name, status (PENDING/ANALYZED/FAILED), insights, insightsText |
| `Post` | type (CAROUSEL/SINGLE_IMAGE/ANIMATION), status (DRAFT/GENERATING/READY/FAILED), content (Json layers) |

### Nano Banana — Gerador de Design

- **Modelo:** `gemini-2.0-flash-lite` com `responseMimeType: 'application/json'`
- **Output:** Array de `DesignState` — cada item tem `format`, `width`, `height`, `backgroundColor`, `layers[]`
- **Layer types:** `text`, `image`, `shape` — cada uma com `x, y, width, height, zIndex, color, fontFamily, fontSize`
- **Dimensões:** carousel/single = 1080×1080; story = 1080×1920

### Ferramentas disponíveis na Fábrica (frontend)

| Tool | Status | Backend |
|---|---|---|
| Gemini (chat) | ✅ Funcional | `/chat` SSE streaming |
| Nano Banana (design) | ✅ Funcional | `/generate-design` |
| Imagem | ⚠️ Stub | Não conectado |
| Animação (vídeo) | ⚠️ Stub | Não conectado |

### Gaps UI ↔ Backend conhecidos

- **Configurações de marca:** páginas `branding/`, `agent/`, `referencias/` têm UI mas **não chamam o backend** — botões "Salvar" são fake
- **Criação de nova marca:** botão sem handler implementado
- **Análise de benchmarks:** frontend usa mock hardcoded, nunca chama `/analyze-benchmark`
- **Rotas protegidas:** `/api/brands` e `/api/ai/*` têm middleware `auth.ts` mas a aplicação de autenticação está incompleta

## Decisões Tomadas

- **Nano Banana** = alias para Gemini 2.0 Flash Lite com API key separada, specializado em geração de JSON de design — separação de keys permite controle de cota independente.
- **JSON mode (`responseMimeType: 'application/json'`)** garante output parseável sem pós-processamento de markdown.
- **Content como `Json` no Prisma** — flexibilidade de schema de layers sem migrations a cada mudança de formato.
- **SSE para chat** em vez de WebSockets — mais simples, suficiente para streaming unidirecional.

## Learnings

- Gemini ainda pode envolver JSON em blocos markdown mesmo com JSON mode — `rawText.replace(/\`\`\`json/g, '')` como fallback em `generate-briefing`.
- Rate limit 429 do Gemini Free Tier ocorre frequentemente — tratar explicitamente com mensagem amigável.
- `ffmpegVideo.ts` existe no frontend mas a tool de Animação ainda é stub — indica intenção futura de exportação de vídeo.

## Relacionados

- [Arquitetura Backend](../architecture/designer-backend.md) — Express, rotas, auth middleware, Prisma
- [Arquitetura Frontend](../architecture/designer-frontend.md) — Next.js App Router, [marca] dynamic routes, CanvasEditor
- [Secretária A.I. (Gabi)](secretaria-ai-gabi.md) — este app é a base do Agente Designer mencionada no diagnóstico
- [Infraestrutura Técnica](../integrations/infraestrutura-tecnica.md) — estado das integrações
