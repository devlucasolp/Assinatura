---
title: Bot 02 — Frontend Renderer DesignDocument
type: workflow
namespace: designer
tags:
  - designer
  - bot-02
  - frontend
  - renderer
  - css
  - designdocument
  - implementacao-paralela
sources:
  - knowledge-base/wiki/architecture/designer/design-document-hibrido.md
  - designer/frontend/src/components/Fabrica/DesignRenderer.tsx
  - designer/frontend/src/components/shared/LayerView.tsx
created: 2026-05-15
updated: 2026-05-15
status: ready-for-implementation
---

# Bot 02 — Frontend Renderer DesignDocument

## Missão

Implementar o renderer frontend de `DesignDocument` com React/CSS seguro, focado em preview profissional por código, sem mexer no editor atual e sem depender da compilação para `Layer[]`.

Este bot trabalha em paralelo com:

- [[bot-01-backend-gemini-designdocument]] — geração backend/Gemini.
- [[bot-03-compat-editor-auditoria-designdocument]] — compatibilidade, auditoria e testes anti-falso-positivo.

## Regra de coordenação paralela

Você está trabalhando em conjunto com outros bots. Não assuma exclusividade do projeto.

### Pode mexer

- `designer/frontend/src/components/DesignDocument/**` — criar.
- `designer/frontend/src/lib/designDocument/**` — criar tipos/helpers frontend.
- `designer/frontend/src/app/[marca]/fabrica/page.tsx` — apenas para preview experimental se necessário e atrás de flag/ramo visual isolado.
- CSS modules novos dentro de `components/DesignDocument`.

### Não mexer

- `designer/backend/**` — reservado ao Bot 01.
- `designer/frontend/src/components/Editor/**` — reservado ao Bot 03.
- `designer/frontend/src/app/[marca]/editor/**` — reservado ao Bot 03.
- `designer/frontend/src/app/[marca]/galeria/**` — reservado ao Bot 03, exceto se combinado explicitamente.
- `DesignRenderer.tsx` atual — não reescrever; pode apenas consultar padrões.

## Objetivo técnico

Criar renderer isolado:

```tsx
<DesignDocumentRenderer document={document} />
```

O renderer deve interpretar uma árvore segura de nodes, sem executar HTML/CSS/JS gerado pelo modelo.

## Todo list

### 1. Criar tipos frontend

- [ ] Criar tipos `DesignDocument`, `DesignTokens`, `DesignPageNode`, `DesignNode`, `ContainerNode`, `TextNode`, `ImageNode`, `ShapeNode`, `Behavior`.
- [ ] Manter nomes compatíveis com o documento do Bot 01.
- [ ] Não importar tipos do backend diretamente.
- [ ] Criar type guards leves para `isDesignDocument()`.

### 2. Criar renderer base

- [ ] Criar `DesignDocumentRenderer.tsx`.
- [ ] Criar `PageNodeView`.
- [ ] Criar `ContainerNodeView`.
- [ ] Criar `TextNodeView`.
- [ ] Criar `ImageNodeView`.
- [ ] Criar `ShapeNodeView`.
- [ ] Criar CSS module isolado.

### 3. CSS seguro

- [ ] Mapear `LayoutStyle` para CSS permitido.
- [ ] Mapear `VisualStyle` para CSS permitido.
- [ ] Bloquear campos desconhecidos.
- [ ] Não usar `dangerouslySetInnerHTML`.
- [ ] Não injetar `<style>` gerado pelo modelo.
- [ ] Não executar JS gerado pelo modelo.
- [ ] Sanitizar URLs de imagem aceitando apenas `data:image/*`, `https://`, `/` ou assets internos permitidos.

### 4. Behaviors controlados

Implementar somente se couber sem risco:

- [ ] `auto-fit-text` usando CSS clamp ou cálculo seguro.
- [ ] `balance-lines` com fallback sem quebrar layout.
- [ ] `smart-contrast` via classes/tokens.
- [ ] `image-focal-point` via `object-position`.

Se algum behavior ficar duvidoso, deixar como TODO no código de forma mínima ou ignorar com fallback seguro.

### 5. Preview experimental

- [ ] Criar componente de demo local com fixture estático.
- [ ] Não depender do endpoint do Bot 01 para compilar.
- [ ] Se integrar na Fábrica, usar fixture/estado experimental sem quebrar geração atual.
- [ ] Garantir que preview antigo de `DesignRenderer` segue funcionando.

## Regra padronizada de entrega

Ao finalizar, entregar relatório com:

```txt
Bot 02 — Entrega
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
- screenshot ou descrição do fixture renderizado
- casos inválidos ignorados/rejeitados

Riscos/pendências:
- ...

Arquivos que NÃO foram tocados:
- backend
- CanvasEditor
- editor routes
```

## Auditoria obrigatória

Antes de declarar pronto:

- [ ] Rodar `npm run lint` em `designer/frontend`.
- [ ] Rodar `npm run build` em `designer/frontend`.
- [ ] Confirmar que a Fábrica atual ainda abre/compila.
- [ ] Confirmar que o Editor atual ainda compila.
- [ ] Confirmar que `DesignRenderer` antigo não foi quebrado.
- [ ] Confirmar que payload com HTML/CSS/JS livre não é executado.

## Testes contra falsos positivos

Não basta renderizar fixture bom. Testar também:

- [ ] Node com `type` desconhecido.
- [ ] Container com `display` inválido.
- [ ] TextNode sem `content`.
- [ ] Imagem com URL `javascript:`.
- [ ] Imagem com URL externa inválida.
- [ ] Node com campo `html`.
- [ ] Node com campo `css`.
- [ ] Node com campo `js`.
- [ ] Layout com width/height negativos.
- [ ] Tokens incompletos.

O renderer deve falhar de forma segura: ignorar node inválido, aplicar fallback visual ou exibir placeholder controlado. Nunca executar conteúdo arbitrário.

## Critério de aceite

- Renderer isolado criado.
- Fixture estático renderiza uma peça visual melhor que layers soltas básicas.
- Sem alteração destrutiva no editor atual.
- Frontend lint/build OK.
- Casos maliciosos não executam código.

## Relacionados

- [[design-document-hibrido]]
- [[designer-frontend]]
- [[render-layout-as-data]]
