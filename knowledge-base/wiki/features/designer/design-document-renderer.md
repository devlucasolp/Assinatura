---
title: Feature — DesignDocument Renderer
namespace: designer
type: feature
tags:
  - designer
  - design-document
  - frontend
  - renderer
  - react
sources:
  - designer/frontend/src/components/Fabrica/DesignDocumentRenderer.tsx
  - designer/frontend/src/lib/design-document-types.ts
created: 2026-05-15
updated: 2026-05-15
status: ✅ estável
---

# Feature — DesignDocument Renderer

## Resumo

O frontend do Designer recebeu a implementação isolada do `DesignDocumentRenderer`. Esta feature introduz a tipagem completa do DesignDocument (incluindo `DesignTokens`, `DesignNode`, e comportamentos permitidos) e provê um componente React seguro para renderizar o design gerado pela IA. Ele garante um preview profissional sem a necessidade de executar HTML, CSS ou JS arbitrários, alinhando-se aos princípios da arquitetura de geração híbrida.

## Detalhes

### Componentes e Tipos
A implementação estabelece os seguintes artefatos principais:
- **`DesignDocument` e Tipos Base:** Tipos TypeScript rigorosos para validação da resposta da IA. Inclui `DesignTokens` (cores, tipografia, espaçamento), `DesignPageNode`, `ContainerNode`, `TextNode`, `ImageNode` e `ShapeNode`.
- **Comportamentos (Behaviors):** Implementados de forma nativa e previsível no React, evitando execução de JS (ex: `auto-fit-text`, `balance-lines`).
- **`DesignDocumentRenderer`:** O componente de preview seguro. Ele recebe a árvore de nós e a mapeia recursivamente para elementos React estilizados de forma controlada via CSS e Tailwind.

### Segurança e Qualidade Visual
O design não confia na IA para calcular z-index absoluto de forma cega, nem renderiza HTML via `dangerouslySetInnerHTML`. O renderer é estrito: se a IA solicitar um layout não suportado, o renderer aplica um fallback seguro.

## Decisões Tomadas

- O `DesignDocumentRenderer` foi implementado como uma camada puramente visual, isolada do CanvasEditor existente, focando em entregar alta fidelidade de design em preview.
- JS/CSS arbitrários não são permitidos; o componente traduz as diretrizes do `DesignDocument` para marcação React limpa.
- Fica estabelecida a fundação para a Fase 1 da arquitetura de DesignDocument Híbrido (Code Preview).

## Learnings

- Construir o renderer antes de integrar com o CanvasEditor ajuda a validar se o modelo Gemini entende corretamente as regras do `DesignDocument` sem poluir a experiência de edição.
- Tipagens fortes são a chave para garantir que o Gemini e o React "falem a mesma língua", atuando como contrato entre os microsserviços do Designer.

## Relacionados

- [[design-document-hibrido]]
- [[bot-02-frontend-renderer-designdocument]]
- [[designer-frontend]]
