---
title: Arquitetura Backend — Designer
type: architecture
tags: [express, prisma, postgresql, typescript, auth, gemini, nano-banana, backend]
sources: [designer/backend/src/app.ts, designer/backend/src/routes/ai.ts, designer/backend/src/middleware/auth.ts, designer/backend/prisma/schema.prisma]
created: 2026-04-22
updated: 2026-04-22
---

# Arquitetura Backend — Designer

## Resumo

API REST em Express + TypeScript, servindo na porta 4000. Conecta ao PostgreSQL via Prisma ORM. Autenticação por JWT. Rotas agrupadas por domínio (`auth`, `brands`, `posts`, `settings`, `ai`, `health`). A lib `nanoBanana.ts` encapsula chamadas ao Gemini para geração de designs em JSON.

## Detalhes

### Stack

| Camada | Tecnologia |
|---|---|
| Runtime | Node.js + TypeScript |
| Framework | Express 5 |
| ORM | Prisma + PostgreSQL |
| Auth | JWT (middleware `auth.ts`) |
| LLM (chat/briefing) | Google Gemini 2.0 Flash Lite (`@google/generative-ai`) |
| LLM (design) | Gemini 2.0 Flash Lite em JSON mode — alias "Nano Banana" |

### Estrutura de rotas

```
POST   /api/auth/login
POST   /api/auth/register

GET    /api/brands
POST   /api/brands
GET    /api/brands/:slug
PUT    /api/brands/:slug
DELETE /api/brands/:slug

GET    /api/posts
POST   /api/posts
GET    /api/posts/:id
PUT    /api/posts/:id

GET    /api/settings
PUT    /api/settings

POST   /api/ai/:slug/chat              ← SSE streaming
POST   /api/ai/:slug/analyze-benchmark
POST   /api/ai/:slug/generate-briefing
POST   /api/ai/:slug/generate-design

GET    /health
```

### Middleware pipeline

```
requestLogger → (auth) → route handler → errorHandler
```

- **`auth.ts`** — verifica Bearer JWT; aplica nas rotas protegidas (brands, posts, ai)
- **`errorHandler.ts`** — centraliza respostas de erro; helper `createError(status, msg, code?)`
- **`requestLogger.ts`** — log de cada request

### nanoBanana.ts — Design Engine

Gemini 2.0 Flash Lite com `responseMimeType: 'application/json'` e system instruction que define regras de layout (z-index, coordenadas relativas à dimensão do formato). Retorna `DesignState[]` — array de slides, cada slide com `layers[]`.

```typescript
interface Layer {
  id: string; type: 'text' | 'image' | 'shape';
  content?: string; url?: string;
  x: number; y: number; width: number; height: number;
  color?: string; fontFamily?: string; fontSize?: number; zIndex: number;
}
interface DesignState {
  format: 'carousel' | 'single' | 'story';
  width: number; height: number; backgroundColor: string; layers: Layer[];
}
```

### Configuração (`config.ts`)

- `DATABASE_URL` — connection string PostgreSQL
- `JWT_SECRET` — segredo para assinar tokens
- `GEMINI_API_KEY` — key para chat + briefing + analyze
- `NANO_BANANA_API_KEY` — key separada para geração de design (controle de cota independente)
- `PORT` — default 4000

## Decisões Tomadas

- **Dois API keys Gemini** — `GEMINI_API_KEY` para chat/análise, `NANO_BANANA_API_KEY` para design. Permite throttle independente e billing separado no futuro.
- **Prisma `Json` field** para `Post.content` — evita migrations a cada iteração do schema de layers.
- **SSE** para `/chat` em vez de WebSocket — simples, nativo no browser, suficiente para streaming unidirecional.

## Learnings

- Gemini pode retornar JSON dentro de bloco markdown mesmo com `responseMimeType: 'application/json'` — aplicar `.replace(/\`\`\`json/g, '')` como fallback.
- Rate limit 429 no Free Tier é frequente; tratar explicitamente antes do `next(error)` genérico.

## Relacionados

- [Agente Designer](../features/agente-designer.md) — feature que usa esta arquitetura
- [Arquitetura Frontend](designer-frontend.md) — cliente desta API
- [Infraestrutura Técnica](../integrations/infraestrutura-tecnica.md) — contexto de implantação
