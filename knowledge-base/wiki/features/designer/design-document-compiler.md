---
title: Feature — Compilação DesignDocument para DesignPage[]
type: feature
namespace: designer
tags:
  - designer
  - design-document
  - compiler
  - frontend
  - canvas-editor
sources:
  - designer/frontend/src/lib/designDocument/compiler.ts
  - designer/frontend/src/lib/designDocument/index.ts
  - designer/frontend/src/lib/designContent.ts
  - designer/frontend/src/app/[marca]/editor/[postId]/page.tsx
  - designer/frontend/src/app/[marca]/editor/page.tsx
  - designer/frontend/src/app/[marca]/galeria/page.tsx
created: 2026-05-15
updated: 2026-05-15
status: active
---

# Feature — Compilação DesignDocument para DesignPage[]

## Resumo

A compilação `DesignDocument -> DesignPage[]` foi documentada como a ponte operacional entre o preview por código seguro e o CanvasEditor atual do Designer. A implementação fica no frontend, dentro de `src/lib/designDocument/compiler.ts`, e transforma a árvore semântica do `DesignDocument` em páginas e layers compatíveis com `DesignRenderer`/`CanvasEditor`.

Essa etapa avança a Fase 2 do [[design-document-hibrido]] sem descartar o editor existente. Posts `hybrid-design` agora podem ser editáveis mesmo quando não trazem `pages` pré-compiladas, desde que o `document` passe no guard `isDesignDocument()` e o compiler consiga gerar `DesignPage[]`.

## Detalhes

### Fluxo documentado

```txt
Post.content kind='hybrid-design'
  -> content.document
  -> isDesignDocument(document)
  -> compileDesignDocumentToPages(document)
  -> DesignPage[]
  -> extractEditablePages(...).status = 'editable'
  -> Editor/Galeria usam o fluxo legado de DesignPage[]
```

### Arquivos frontend alterados/citados

- `designer/frontend/src/lib/designDocument/compiler.ts` — cria `compileDesignDocumentToPages(document)` e converte nodes semânticos para layers.
- `designer/frontend/src/lib/designDocument/index.ts` — exporta o compiler e o tipo `CompileDesignDocumentResult` para o restante do frontend.
- `designer/frontend/src/lib/designContent.ts` — integra o compiler no `extractEditablePages()` e adiciona a origem `compiled-document` para conteúdos híbridos sem `pages` salvas.
- `designer/frontend/src/app/[marca]/editor/[postId]/page.tsx` — consome `extractEditablePages()` para abrir posts editáveis no CanvasEditor.
- `designer/frontend/src/app/[marca]/editor/page.tsx` — filtra posts editáveis usando a mesma extração centralizada.
- `designer/frontend/src/app/[marca]/galeria/page.tsx` — usa `extractPreviewSource()`/`DesignRenderer` para thumbnails e preview de designs compilados.

### Comportamento técnico

- O compiler rejeita documentos inválidos retornando `null`, preservando falha segura.
- Cada página do `DesignDocument` vira uma `DesignPage` com `width`, `height`, `backgroundColor` e `layers`.
- `TextNode`, `ImageNode`, `ShapeNode` e `ContainerNode` são convertidos para layers compatíveis com o renderer/editor atual.
- Layouts usam resolução defensiva de tamanho (`number`, `%`, `px`) e clamp para evitar dimensões negativas ou fora do canvas.
- URLs de imagem passam por `sanitizeImageUrl()`; imagens ausentes ou bloqueadas viram warning e não geram layer.
- Containers com fundo/borda/sombra visíveis geram layer de shape base e depois compilam filhos em fluxo simples.
- O resultado inclui `warnings`, propagados por `extractEditablePages()` quando a origem é `compiled-document`.

### Relação com formatos existentes

`extractEditablePages()` preserva a precedência de compatibilidade:

1. `DesignPage[]` legado continua editável como `legacy-pages`.
2. `hybrid-design.pages` válido continua preferido como `hybrid-pages`.
3. Se não houver `pages`, o frontend tenta `compileDesignDocumentToPages(content.document)`.
4. Se a compilação falhar, o conteúdo permanece como `hybrid-uncompiled` e não abre CanvasEditor vazio.
5. Posts de imagem continuam sendo convertidos para uma `DesignPage` simples via `image-post`.

## Decisões Tomadas

- A primeira compilação roda no frontend para destravar Editor/Galeria sem depender imediatamente do backend salvar `pages` junto com `document`.
- O formato canônico de edição continua sendo `DesignPage[]`/`Layer[]`; o `DesignDocument` permanece a fonte semântica rica.
- `hybrid-design.pages` pré-existente tem prioridade sobre recompilar o documento, evitando sobrescrever uma versão já materializada.
- A compilação deve falhar de forma explícita e segura (`null`/warnings), nunca inventando layers a partir de payload inválido.

## Learnings

- A ponte de compatibilidade reduz o risco da arquitetura híbrida porque permite evoluir geração por código sem bloquear o CanvasEditor.
- O compiler precisa ser conservador: é melhor perder um node inválido com warning do que abrir canvas quebrado ou aceitar falso positivo.
- A separação entre `DesignDocumentRenderer` e compiler é importante: o renderer valida qualidade visual por código; o compiler materializa uma versão editável para o editor atual.

## Relacionados

- [[design-document-hibrido]]
- [[design-document-renderer]]
- [[bot-02-frontend-renderer-designdocument]]
- [[bot-03-compat-editor-auditoria-designdocument]]
- [[designer-frontend]]
- [[agente-designer]]
