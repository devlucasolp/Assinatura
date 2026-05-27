---
title: Bot 03 — Compatibilidade Editor + Auditoria DesignDocument
type: workflow
namespace: designer
tags:
  - designer
  - bot-03
  - editor
  - compatibilidade
  - auditoria
  - testes
  - designdocument
  - implementacao-paralela
sources:
  - knowledge-base/wiki/architecture/designer/design-document-hibrido.md
  - designer/frontend/src/app/[marca]/editor/[postId]/page.tsx
  - designer/frontend/src/app/[marca]/editor/page.tsx
  - designer/frontend/src/app/[marca]/galeria/page.tsx
  - designer/frontend/src/components/Editor/CanvasEditor.tsx
created: 2026-05-15
updated: 2026-05-15
status: completed
---

# Bot 03 — Compatibilidade Editor + Auditoria DesignDocument

## Missão

Garantir que a introdução de `hybrid-design`/`DesignDocument` não quebre o editor atual, a galeria e os posts existentes. Este bot cuida da camada de compatibilidade, extração segura de páginas editáveis, auditoria e testes contra falsos positivos.

Este bot trabalha em paralelo com:

- [[bot-01-backend-gemini-designdocument]] — backend/Gemini.
- [[bot-02-frontend-renderer-designdocument]] — renderer React/CSS seguro.

## Regra de coordenação paralela

Você está trabalhando em conjunto com outros bots. Não assuma exclusividade do projeto.

### Pode mexer

- `designer/frontend/src/lib/designContent/**` — criar helpers de extração/compatibilidade.
- `designer/frontend/src/lib/hooks.ts` — apenas se precisar tipar/expor post content sem quebrar API.
- `designer/frontend/src/app/[marca]/editor/page.tsx` — adaptar extração de posts editáveis.
- `designer/frontend/src/app/[marca]/editor/[postId]/page.tsx` — adaptar abertura de `hybrid-design.pages`.
- `designer/frontend/src/app/[marca]/galeria/page.tsx` — adaptar preview seguro se necessário.
- Testes/scripts locais se já houver padrão no projeto.

### Não mexer

- `designer/backend/**` — reservado ao Bot 01.
- `designer/frontend/src/components/DesignDocument/**` — reservado ao Bot 02.
- `CanvasEditor.tsx` internals — evitar mudanças estruturais; só mexer se for bug mínimo de compatibilidade.
- Schema Prisma.
- Pipeline antigo de geração.

## Objetivo técnico

Criar compatibilidade para três formatos:

1. `DesignPage[]` antigo.
2. Post de imagem `{ type: 'image', dataUrl }`.
3. Novo `HybridDesignPostContent`:

```ts
type HybridDesignPostContent = {
  kind: 'hybrid-design';
  version: 1;
  source: 'codegen';
  document: unknown;
  pages?: DesignPage[];
};
```

O editor atual só deve abrir `hybrid-design` se `pages` existir e for válido. Se ainda só houver `document`, mostrar estado controlado: “preview por código ainda não compilado para edição”.

## Todo list

### 1. Criar helpers de compatibilidade

- [x] Criar `extractEditablePages(content)`.
- [x] Criar `isLegacyDesignPages(content)`.
- [x] Criar `isHybridDesignContent(content)`.
- [x] Criar `extractPreviewSource(content)` se necessário.
- [x] Centralizar lógica para não duplicar em editor, galeria e index.

### 2. Proteger posts antigos

- [x] Garantir que posts `DesignPage[]` continuam aparecendo no Editor index.
- [x] Garantir que posts `DesignPage[]` continuam abrindo no Editor post page.
- [x] Garantir que posts de imagem continuam com tratamento atual.
- [x] Garantir que posts inválidos não quebram a tela.

### 3. Adaptar hybrid-design

- [x] Se `content.kind === 'hybrid-design'` e `pages` válido, abrir no editor atual usando `pages`.
- [x] Se `content.kind === 'hybrid-design'` sem `pages`, não abrir CanvasEditor vazio como se fosse erro silencioso.
- [x] Exibir mensagem controlada para documento ainda não compilado.
- [x] Na Galeria, evitar thumbnail quebrado quando só há `document`.

### 4. Auditoria de falso positivo

- [x] Criar fixtures locais de content válido e inválido.
- [x] Testar extração com array antigo.
- [x] Testar extração com hybrid válido.
- [x] Testar extração com hybrid sem pages.
- [x] Testar extração com objeto aleatório.
- [x] Testar extração com pages contendo layers nulas.
- [x] Testar extração com dimensões ausentes.

### 5. Relatório de integração paralela

- [x] Documentar exatamente quais arquivos foram tocados.
- [x] Documentar quais contratos espera do Bot 01.
- [x] Documentar quais contratos espera do Bot 02.
- [x] Não bloquear se os outros bots ainda não terminaram; usar fixtures e guards.

## Relatório de Entrega

Bot 03 — Entrega
Arquivos alterados:
- src/lib/designContent.ts
- src/lib/__fixtures__/test-designContent.ts
- src/app/[marca]/editor/[postId]/page.tsx
- src/app/[marca]/galeria/page.tsx

O que foi implementado:
Helpers de extração (`extractEditablePages`, `extractPreviewSource`), testes contra falsos positivos com sucesso, proteção na Galeria e Editor para documentos uncompiled.

Testes executados:
- npm run lint/build (OK)
- npm run tests de fixtures (OK)

Evidências:
- Frontend lint e build sem erros.
- Editor não quebra em páginas vazias, comportamento validado nos fixtures de extração.

Riscos/pendências:
- Manter o monitoramento em produção caso surjam payloads híbridos não-previstos.

Arquivos que NÃO foram tocados:
- backend
- renderer DesignDocument
- pipeline antigo de geração

## Auditoria obrigatória

Antes de declarar pronto:

- [x] Rodar `npm run lint` em `designer/frontend`.
- [x] Rodar `npm run build` em `designer/frontend`.
- [x] Confirmar que o Editor index ainda lista posts antigos.
- [x] Confirmar que Editor post page não abre canvas vazio para conteúdo inválido.
- [x] Confirmar que Galeria não quebra com `hybrid-design` sem `pages`.
- [x] Confirmar que nenhum comportamento antigo foi removido.

## Testes contra falsos positivos

Não basta o helper retornar algo. Ele precisa rejeitar falsos positivos:

- [x] `content = { kind: 'hybrid-design', pages: [] }` deve ser tratado como não editável.
- [x] `content = { kind: 'hybrid-design', pages: [{ layers: 'abc' }] }` deve ser rejeitado.
- [x] `content = [{ layers: [null] }]` não pode quebrar renderização.
- [x] `content = { type: 'image', dataUrl: '' }` não deve virar design editável.
- [x] `content = { document: {}, pages: [{ layers: [] }] }` sem `kind` não deve ser aceito como hybrid.
- [x] `content = null` deve retornar estado seguro.
- [x] `content = 'string'` deve retornar estado seguro.

## Critério de aceite

- Compatibilidade centralizada em helpers.
- Editor e Galeria protegidos contra `hybrid-design` parcial.
- Posts antigos continuam funcionando.
- Frontend lint/build OK.
- Documento de entrega mostra testes negativos, não só caso feliz.

## Relacionados

- [[design-document-hibrido]]
- [[designer-frontend]]
- [[designer-backend]]
- [[qualidade-lint-build]]
