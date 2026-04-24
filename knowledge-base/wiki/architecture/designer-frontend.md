---
title: Arquitetura Frontend — Designer
type: architecture
tags: [next.js, react, typescript, app-router, canvas-editor, branding, dynamic-routes, sse]
sources: [designer/frontend/src/app/[marca]/fabrica/page.tsx, designer/frontend/src/lib/api.ts, designer/frontend/src/components/Editor/CanvasEditor.tsx, designer/frontend/AGENTS.md]
created: 2026-04-22
updated: 2026-04-22
---

# Arquitetura Frontend — Designer

## Resumo

Next.js com App Router e TypeScript. A rota dinâmica `[marca]` isola o contexto de cada brand — todas as páginas dentro dela recebem o `slug` da marca via `useParams()`. A "Fábrica" é o hub de criação (chat com IA + Nano Banana). O CanvasEditor renderiza e edita as camadas geradas. Comunicação com backend em `localhost:4000` via `fetch` + SSE para streaming.

## Detalhes

### Estrutura de páginas

```
/                          ← landing / redirect
/login                     ← autenticação
/galeria                   ← galeria global de posts

/[marca]/
  configuracoes/           ← hub de config da marca
    branding/              ← cores, fontes, logo ⚠️ sem handler de save
    agent/                 ← agentPrompt, guidelines ⚠️ sem handler de save
    referencias/           ← benchmarks ⚠️ usa mock, não chama backend
  fabrica/                 ← chat IA (Gemini + Nano Banana)
  editor/                  ← canvas editor de layers
  galeria/                 ← galeria de posts da marca

/extras/docs/              ← documentação interna
```

### Componentes principais

| Componente | Localização | Papel |
|---|---|---|
| `AppShell` | `components/AppShell/` | Layout base com sidebar + conteúdo |
| `Sidebar` | `components/Sidebar/` | Navegação entre seções da marca |
| `CanvasEditor` | `components/Editor/CanvasEditor.tsx` | Renderiza e edita `DesignState` (layers) |
| `Button`, `Card`, `Input`, `PageHeader` | `components/ui/` | Design system interno |

### Fábrica — fluxo de chat

1. Usuário seleciona ferramenta (Gemini / Nano Banana / Imagem / Animação)
2. `sendMessage()` faz `POST /api/ai/:slug/chat` ou `/generate-design`
3. Para Gemini: lê SSE stream, atualiza mensagem chunk a chunk (estado React)
4. Para Nano Banana: espera JSON, exibe link para galeria/editor
5. Image e Animação: stubs com timeout de simulação — **não conectados ao backend**

### Autenticação no frontend

- Token JWT guardado em `localStorage` como `auth_token`
- Enviado como `Authorization: Bearer <token>` em cada request
- `middleware.ts` na raiz do Next.js controla redirecionamentos de rota

### Libs auxiliares

| Arquivo | Uso |
|---|---|
| `src/lib/api.ts` | Wrapper de fetch para o backend |
| `src/lib/hooks.ts` | Custom hooks React |
| `src/lib/ffmpegVideo.ts` | Exportação de vídeo — **não implementada, prevista para Animação** |

### Nota sobre a versão do Next.js

O `AGENTS.md` avisa: *"This is NOT the Next.js you know — breaking changes may apply. Read `node_modules/next/dist/docs/` before writing code."* Versão pode não ser a 15 canônica — checar `package.json` antes de usar APIs de router/cache.

## Decisões Tomadas

- **`[marca]` dynamic route** como escopo — cada marca é isolada sem estado global, simplifica multi-tenancy.
- **SSE em vez de WebSocket** — nativo no browser via `fetch + ReadableStream`, zero dependências extras.
- **localStorage para token** — trade-off: simples de implementar, menos seguro que httpOnly cookie. Aceitável para MVP.

## Learnings

- `ffmpegVideo.ts` indica intenção de exportação de vídeo futura — não bloquear mudanças no `CanvasEditor` que quebraria esse export.
- As páginas de configuração têm UI completa mas handlers de save ausentes — risco de usuário pensar que salvou e não salvou. Prioridade de correção alta.

## Relacionados

- [Agente Designer](../features/agente-designer.md) — feature que usa esta arquitetura
- [Arquitetura Backend](designer-backend.md) — API que o frontend consome
