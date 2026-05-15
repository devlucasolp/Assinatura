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
status: ✅ concluído
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

- [ ] Criar `extractEditablePages(content)`.
- [ ] Criar `isLegacyDesignPages(content)`.
- [ ] Criar `isHybridDesignContent(content)`.
- [ ] Criar `extractPreviewSource(content)` se necessário.
- [ ] Centralizar lógica para não duplicar em editor, galeria e index.

### 2. Proteger posts antigos

- [ ] Garantir que posts `DesignPage[]` continuam aparecendo no Editor index.
- [ ] Garantir que posts `DesignPage[]` continuam abrindo no Editor post page.
- [ ] Garantir que posts de imagem continuam com tratamento atual.
- [ ] Garantir que posts inválidos não quebram a tela.

### 3. Adaptar hybrid-design

- [ ] Se `content.kind === 'hybrid-design'` e `pages` válido, abrir no editor atual usando `pages`.
- [ ] Se `content.kind === 'hybrid-design'` sem `pages`, não abrir CanvasEditor vazio como se fosse erro silencioso.
- [ ] Exibir mensagem controlada para documento ainda não compilado.
- [ ] Na Galeria, evitar thumbnail quebrado quando só há `document`.

### 4. Auditoria de falso positivo

- [ ] Criar fixtures locais de content válido e inválido.
- [ ] Testar extração com array antigo.
- [ ] Testar extração com hybrid válido.
- [ ] Testar extração com hybrid sem pages.
- [ ] Testar extração com objeto aleatório.
- [ ] Testar extração com pages contendo layers nulas.
- [ ] Testar extração com dimensões ausentes.

### 5. Relatório de integração paralela

- [ ] Documentar exatamente quais arquivos foram tocados.
- [ ] Documentar quais contratos espera do Bot 01.
- [ ] Documentar quais contratos espera do Bot 02.
- [ ] Não bloquear se os outros bots ainda não terminaram; usar fixtures e guards.

## Regra padronizada de entrega

Ao finalizar, entregar relatório com:

```txt
Bot 03 — Entrega
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
- lista de fixtures testadas
- comportamento para hybrid sem pages

Riscos/pendências:
- ...

Arquivos que NÃO foram tocados:
- backend
- renderer DesignDocument
- pipeline antigo de geração
```

## Auditoria obrigatória

Antes de declarar pronto:

- [ ] Rodar `npm run lint` em `designer/frontend`.
- [ ] Rodar `npm run build` em `designer/frontend`.
- [ ] Confirmar que o Editor index ainda lista posts antigos.
- [ ] Confirmar que Editor post page não abre canvas vazio para conteúdo inválido.
- [ ] Confirmar que Galeria não quebra com `hybrid-design` sem `pages`.
- [ ] Confirmar que nenhum comportamento antigo foi removido.

## Testes contra falsos positivos

Não basta o helper retornar algo. Ele precisa rejeitar falsos positivos:

- [ ] `content = { kind: 'hybrid-design', pages: [] }` deve ser tratado como não editável.
- [ ] `content = { kind: 'hybrid-design', pages: [{ layers: 'abc' }] }` deve ser rejeitado.
- [ ] `content = [{ layers: [null] }]` não pode quebrar renderização.
- [ ] `content = { type: 'image', dataUrl: '' }` não deve virar design editável.
- [ ] `content = { document: {}, pages: [{ layers: [] }] }` sem `kind` não deve ser aceito como hybrid.
- [ ] `content = null` deve retornar estado seguro.
- [ ] `content = 'string'` deve retornar estado seguro.

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
