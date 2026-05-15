---
title: Bot 01 — Backend Gemini + DesignDocument
type: workflow
namespace: designer
tags:
  - designer
  - bot-01
  - backend
  - gemini
  - designdocument
  - implementacao-paralela
sources:
  - knowledge-base/wiki/architecture/designer/design-document-hibrido.md
  - designer/backend/src/routes/ai.ts
  - designer/backend/src/lib/nanoBanana.ts
created: 2026-05-15
updated: 2026-05-15
status: ready-for-implementation
---

# Bot 01 — Backend Gemini + DesignDocument

## Missão

Implementar a base backend da geração por `DesignDocument`, usando Gemini com inteligência pesada e contexto ampliado, sem quebrar o pipeline atual de `DesignState`/`Layer[]`.

Este bot trabalha em paralelo com:

- [[bot-02-frontend-renderer-designdocument]] — renderer React/CSS seguro.
- [[bot-03-compat-editor-auditoria-designdocument]] — compatibilidade com editor, auditoria e testes anti-falso-positivo.

## Regra de coordenação paralela

Você está trabalhando em conjunto com outros bots. Não assuma exclusividade do projeto.

### Pode mexer

- `designer/backend/src/lib/designDocument/**` — criar.
- `designer/backend/src/lib/designDocument.ts` — criar se preferir arquivo único inicial.
- `designer/backend/src/routes/ai.ts` — apenas para adicionar endpoint experimental e wiring mínimo.
- `designer/backend/src/lib/geminiRetry.ts` — somente se precisar reaproveitar sem quebrar API atual.
- `designer/backend/src/config.ts` — somente se precisar declarar modelo/env opcional de forma compatível.

### Não mexer

- `designer/frontend/**` — reservado aos Bots 02 e 03.
- `designer/backend/src/lib/nanoBanana.ts` — não reescrever; apenas importar/reusar se necessário.
- `designer/backend/prisma/schema.prisma` — proibido nesta fase.
- Rotas existentes de geração (`generate-design`, `create-job`) — não alterar comportamento existente.
- CanvasEditor, Galeria e componentes de UI.

## Objetivo técnico

Criar um caminho experimental:

```txt
POST /api/ai/:slug/generate-design-document
  ↓
resolve Brand + BrandConfig + referências
  ↓
Gemini pesado gera HybridDesignPostContent
  ↓
validação estrutural
  ↓
retorna document sem salvar ou salva como draft experimental, conforme menor risco
```

Preferência inicial: **retornar o `document` sem persistir**, para reduzir risco. Persistência entra depois da revisão técnica.

## Todo list

### 1. Criar tipos backend

- [ ] Criar tipos `DesignDocument`, `DesignTokens`, `DesignPageNode`, `DesignNode`, `ContainerNode`, `TextNode`, `ImageNode`, `ShapeNode`, `Behavior`.
- [ ] Criar tipo `HybridDesignPostContent`.
- [ ] Incluir `version: 1` obrigatório.
- [ ] Manter compatibilidade conceitual com `DesignPage[]`, mas sem depender do frontend.

### 2. Criar validador defensivo

- [ ] Validar `kind === 'hybrid-design'`.
- [ ] Validar `document.version === 1`.
- [ ] Validar `width`, `height`, `format`.
- [ ] Validar que `pages` é array não vazio.
- [ ] Validar que todo node tem `id` e `type` permitido.
- [ ] Remover/recusar qualquer campo de HTML, CSS ou JS livre.
- [ ] Recusar nodes com `script`, `styleRaw`, `dangerouslySetInnerHTML`, `html`, `css`, `js`.

### 3. Criar prompt Gemini pesado

- [ ] Criar `generateDesignDocument()`.
- [ ] Usar modelo pesado configurável, preferencialmente Gemini Pro/Thinking quando disponível.
- [ ] Fallback para modelo atual apenas se variável de modelo pesado não estiver definida.
- [ ] Contexto obrigatório:
  - [ ] Brand name/slug.
  - [ ] BrandConfig agentPrompt/guidelines/colors/fonts/logo.
  - [ ] referências analisadas quando disponíveis.
  - [ ] briefing do usuário.
  - [ ] formato/dimensões/quantidade de slides.
  - [ ] templates permitidos.
  - [ ] tokens obrigatórios.
  - [ ] checklist de crítica visual.
- [ ] Instruir o modelo a agir como diretor de arte, não como desenhista de pixels.

### 4. Criar endpoint experimental

- [ ] Adicionar `POST /api/ai/:slug/generate-design-document`.
- [ ] Proteger com auth existente.
- [ ] Validar ownership usando o mesmo padrão das rotas atuais.
- [ ] Não quebrar nenhuma rota existente.
- [ ] Retornar JSON validado com `data.document` ou `data.content`.
- [ ] Em erro de validação, retornar mensagem clara e log seguro.

### 5. Fallback e segurança

- [ ] Se Gemini retornar JSON inválido, tentar sanitização mínima uma vez.
- [ ] Se continuar inválido, retornar erro controlado sem salvar post.
- [ ] Não logar secrets, API keys, tokens ou payload base64 grande.
- [ ] Limitar tamanho de prompt/contexto.

## Regra padronizada de entrega

Ao finalizar, entregar relatório com:

```txt
Bot 01 — Entrega
Arquivos alterados:
- ...

O que foi implementado:
- ...

Como testar:
- comando 1
- comando 2

Evidências:
- saída do lint
- saída do build
- exemplo de payload válido
- exemplo de payload inválido rejeitado

Riscos/pendências:
- ...

Arquivos que NÃO foram tocados:
- frontend
- CanvasEditor
- rotas antigas de geração
```

## Auditoria obrigatória

Antes de declarar pronto:

- [ ] Rodar `npm run lint` em `designer/backend`.
- [ ] Rodar `npm run build` em `designer/backend`.
- [ ] Confirmar que rotas antigas continuam compilando.
- [ ] Confirmar que endpoint novo exige autenticação.
- [ ] Confirmar que endpoint novo valida ownership da brand.
- [ ] Confirmar que payload com CSS/JS livre é rejeitado.
- [ ] Confirmar que erro de Gemini não salva post parcial.

## Testes contra falsos positivos

Não basta testar o caso feliz. Testar também:

- [ ] Gemini retorna markdown com JSON dentro de bloco ```json.
- [ ] Gemini retorna `html`, `css`, `js` ou `script` no payload.
- [ ] Gemini retorna node sem `id`.
- [ ] Gemini retorna `type` desconhecido.
- [ ] Gemini retorna `pages: []`.
- [ ] Brand inexistente.
- [ ] Brand existente de outro usuário.
- [ ] Prompt vazio.
- [ ] Modelo pesado indisponível.

O bot só pode marcar como pronto se os falsos positivos forem rejeitados de forma explícita.

## Critério de aceite

- Endpoint experimental disponível e isolado.
- Tipos e validador criados.
- Gemini pesado/contexto ampliado documentado no código via nomes claros, sem comentários desnecessários.
- Nenhuma rota existente quebrada.
- Backend lint/build OK.

## Relacionados

- [[design-document-hibrido]]
- [[designer-backend]]
- [[agente-multimodelo]]
- [[render-layout-as-data]]
