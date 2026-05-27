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
status: completed
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

- [x] Criar tipos `DesignDocument`, `DesignTokens`, `DesignPageNode`, `DesignNode`, `ContainerNode`, `TextNode`, `ImageNode`, `ShapeNode`, `Behavior`.
- [x] Manter nomes compatíveis com o documento do Bot 01.
- [x] Não importar tipos do backend diretamente.
- [x] Criar type guards leves para `isDesignDocument()`.

### 2. Criar renderer base

- [x] Criar `DesignDocumentRenderer.tsx`.
- [x] Criar `PageNodeView`.
- [x] Criar `ContainerNodeView`.
- [x] Criar `TextNodeView`.
- [x] Criar `ImageNodeView`.
- [x] Criar `ShapeNodeView`.
- [x] Criar CSS module isolado.

### 3. CSS seguro

- [x] Mapear `LayoutStyle` para CSS permitido.
- [x] Mapear `VisualStyle` para CSS permitido.
- [x] Bloquear campos desconhecidos.
- [x] Não usar `dangerouslySetInnerHTML`.
- [x] Não injetar `<style>` gerado pelo modelo.
- [x] Não executar JS gerado pelo modelo.
- [x] Sanitizar URLs de imagem aceitando apenas `data:image/*`, `https://`, `/` ou assets internos permitidos.

### 4. Behaviors controlados

Implementar somente se couber sem risco:

- [x] `auto-fit-text` usando CSS clamp ou cálculo seguro.
- [x] `balance-lines` com fallback sem quebrar layout.
- [x] `smart-contrast` via classes/tokens.
- [x] `image-focal-point` via `object-position`.

Se algum behavior ficar duvidoso, deixar como TODO no código de forma mínima ou ignorar com fallback seguro.

### 5. Preview experimental

- [x] Criar componente de demo local com fixture estático.
- [x] Não depender do endpoint do Bot 01 para compilar.
- [x] Se integrar na Fábrica, usar fixture/estado experimental sem quebrar geração atual.
- [x] Garantir que preview antigo de `DesignRenderer` segue funcionando.

## Relatório de Entrega

Bot 02 — Entrega
Arquivos alterados:
- src/lib/designDocument/* (types, styles, guards, index)
- src/components/DesignDocument/DesignDocumentRenderer.tsx
- src/components/DesignDocument/DesignDocumentRenderer.module.css

O que foi implementado:
Tipagem segura de DesignDocument, mapeamento de estilos e behaviors, renderer isolado e sem dangerouslySetInnerHTML, preview demo.

Testes executados:
- npm run lint
- npm run build (OK)
- tsx test-design-document.ts testando casos inválidos e maliciosos (URLs de javascript, tipos desconhecidos) não executam código.

Evidências:
- Frontend lint e build sem erros.
- Documentos inválidos ou maliciosos são ignorados e não afetam o runtime.

Riscos/pendências:
- Avaliar a necessidade de integração completa do render no fluxo final do Editor após compilação.

Arquivos que NÃO foram tocados:
- backend
- CanvasEditor
- editor routes

## Auditoria obrigatória

Antes de declarar pronto:

- [x] Rodar `npm run lint` em `designer/frontend`.
- [x] Rodar `npm run build` em `designer/frontend`.
- [x] Confirmar que a Fábrica atual ainda abre/compila.
- [x] Confirmar que o Editor atual ainda compila.
- [x] Confirmar que `DesignRenderer` antigo não foi quebrado.
- [x] Confirmar que payload com HTML/CSS/JS livre não é executado.

## Testes contra falsos positivos

Não basta renderizar fixture bom. Testar também:

- [x] Node com `type` desconhecido.
- [x] Container com `display` inválido.
- [x] TextNode sem `content`.
- [x] Imagem com URL `javascript:`.
- [x] Imagem com URL externa inválida.
- [x] Node com campo `html`.
- [x] Node com campo `css`.
- [x] Node com campo `js`.
- [x] Layout com width/height negativos.
- [x] Tokens incompletos.

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
