---
title: Agente Designer
type: feature
tags: [designer, gemini, nano-banana, next.js, express, prisma, canvas-editor, branding, posts]
sources: [designer/backend/src/routes/ai.ts, designer/backend/src/lib/nanoBanana.ts, designer/frontend/src/app/[marca]/fabrica/page.tsx, designer/backend/prisma/schema.prisma]
created: 2026-04-22
updated: 2026-04-25
---

# Agente Designer

## Resumo

App web de geração de designs visuais com IA, construído em Next.js (frontend) + Express (backend) + PostgreSQL via Prisma. Cada marca tem seu próprio agente configurado (guidelines, prompt, cores, fontes). O usuário descreve o que quer na "Fábrica" e o backend chama o Nano Banana (Gemini 2.5 Flash Lite) que devolve um JSON de camadas (layers); o editor visual renderiza e exporta as camadas. Sprint 0 concluído em 2026-04-25: SDK migrado para `@google/genai`, modelos atualizados para Gemini 2.5, tool Imagem conectada, export PNG funcional.

## Detalhes

### Fluxo Principal (Fábrica → Design)

```
Usuário descreve no chat (Fábrica page)
  → POST /api/ai/:slug/generate-design
    → getBrandContext(slug)         ← BrandConfig no Postgres
    → generateDesign() [nanoBanana.ts]
      → Gemini 2.5 Flash Lite (JSON mode)
      → retorna DesignState[] (array de slides com layers)
    → prisma.post.create (status: DRAFT, content: Json)
  → frontend exibe link para galeria/editor

Fluxo alternativo — Tool Imagem:
  → POST /api/ai/:slug/generate-image
    → getBrandContext(slug)
    → Gemini 2.5 Flash Image (responseModalities: ['IMAGE'])
    → extrai base64 da resposta
    → prisma.post.create (status: READY, content: { type: 'image', dataUrl })
    → resposta inclui dataUrl inline
  → frontend exibe imagem no chat + link para editor
```

### Endpoints de IA (`/api/ai/:slug/`)

| Endpoint | Método | Descrição |
|---|---|---|
| `/:slug/chat` | POST | Chat streaming com Gemini (SSE) — usa brand context como system instruction |
| `/:slug/analyze-benchmark` | POST | Análise de referência/concorrente → insights em Markdown |
| `/:slug/generate-briefing` | POST | Gera guidelines + agentPrompt + suggestedColors (JSON) |
| `/:slug/generate-design` | POST | Gera DesignState[] via Nano Banana → salva como Post DRAFT |
| `/:slug/generate-image` | POST | Gera imagem via Gemini 2.5 Flash Image → salva como Post READY com dataUrl |

### Modelos de Dados (Prisma)

| Model | Campos principais |
|---|---|
| `User` | id, email, password, name, role (ADMIN/DESIGNER) |
| `Brand` | id, slug, name, color, userId |
| `BrandConfig` | agentPrompt, primaryFonts, colors[], guidelines, logoUrl — 1:1 com Brand |
| `Reference` | name, status (PENDING/ANALYZED/FAILED), insights, insightsText |
| `Post` | type (CAROUSEL/SINGLE_IMAGE/ANIMATION), status (DRAFT/GENERATING/READY/FAILED), content (Json layers) |

### Nano Banana — Gerador de Design

- **Modelo:** `gemini-2.5-flash-lite` com `responseMimeType: 'application/json'`
- **Output:** Array de `DesignState` — cada item tem `format`, `width`, `height`, `backgroundColor`, `layers[]`
- **Layer types:** `text`, `image`, `shape` — cada uma com `x, y, width, height, zIndex, color, fontFamily, fontSize`
- **Dimensões:** carousel/single = 1080×1080; story = 1080×1920

### Ferramentas disponíveis na Fábrica (frontend)

| Tool | Status | Backend |
|---|---|---|
| Gemini (chat) | ✅ Funcional | `/chat` SSE streaming |
| Nano Banana (design) | ✅ Funcional | `/generate-design` |
| Imagem | ✅ Conectado (Sprint 0) | `/generate-image` — Gemini 2.5 Flash Image |
| Animação (vídeo) | ⚠️ Stub | Não conectado — `ffmpegVideo.ts` existe mas não chamado |

### Gaps UI ↔ Backend — Estado Atual (2026-04-25)

> ⚠️ **Correção:** a afirmação anterior de que as páginas de configuração "não chamam o backend" estava incorreta. As páginas `branding/`, `agent/` e `referencias/` já chamavam o backend corretamente antes do Sprint 0.

- **Configurações de marca:** páginas `branding/` e `agent/` chamam `PUT /api/settings/:slug/config` corretamente. `referencias/` tem CRUD completo com análise em background via Gemini.
- **Post de imagem no editor:** quando a Gabi abre no editor um post gerado pela tool Imagem, o canvas fica vazio — o editor faz `content.layers || []` mas posts de imagem têm `content.type === 'image'`, sem `layers`. **Aberto.**
- **Markdown nos balões da Fábrica:** links `[Editor](...)` são exibidos como texto literal. Gabi não consegue clicar diretamente. **Aberto.**
- **Toast de feedback:** saves de configuração funcionam mas não exibem confirmação visual. **Aberto.**
- **Ownership check ausente:** qualquer usuário autenticado pode ler/escrever config de qualquer marca pelo slug. **Gap de segurança aberto.**
- **Criação de nova marca:** botão sem handler implementado. **Aberto.**

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
