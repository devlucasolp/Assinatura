---
title: Arquitetura — DesignDocument Híbrido
namespace: designer
type: architecture
tags:
  - designer
  - design-document
  - codegen
  - css
  - javascript
  - gemini
  - canvas-editor
  - containers
sources:
  - designer/backend/src/lib/nanoBanana.ts
  - designer/backend/src/routes/ai.ts
  - designer/frontend/src/components/Fabrica/DesignRenderer.tsx
  - designer/frontend/src/components/Editor/CanvasEditor.tsx
  - knowledge-base/wiki/decisions/adr-006-editor-visual-alternativas-canva.md
created: 2026-05-15
updated: 2026-05-15
status: 🔄 em evolução
---

# Arquitetura — DesignDocument Híbrido

## Resumo

Direção proposta para evoluir a geração visual do Designer sem perder o trabalho já feito no CanvasEditor. O objetivo é mesclar a qualidade de design por código/CSS/JS controlado com uma edição posterior conteinerizada. A IA deixa de ser responsável por calcular todos os pixels e passa a gerar um documento semântico de design; o código do produto renderiza, compila e, em etapa posterior, transforma blocos em containers editáveis.

## Problema

A geração atual usa `DesignState`/`Layer[]` com coordenadas absolutas. Esse formato é editável e compatível com o CanvasEditor, mas tende a produzir design menos profissional porque força o modelo a desenhar por pixels, z-index e caixas soltas.

Ferramentas de design por código tendem a gerar resultados melhores porque raciocinam em termos de estrutura visual: grid, flex, seções, hierarquia, componentes, tokens, espaçamento, contraste, ritmo e CSS. O navegador ou renderer resolve layout melhor do que o LLM calculando coordenadas absolutas.

## Decisão proposta

Criar uma camada intermediária chamada `DesignDocument`, que funciona como código visual seguro e declarativo.

Fluxo-alvo:

```txt
Briefing + BrandContext + referências
  ↓
Gemini pesado com contexto ampliado
  ↓
DesignDocument semântico
  ↓
DesignDocumentRenderer React/CSS
  ↓
compileDesignDocumentToPages()
  ↓
DesignPage[] / Layer[] compatível com CanvasEditor
  ↓
Editor atual agora; editor containerizado depois
```

A primeira versão deve focar em renderização por código e preview profissional. A conversão para formatos mais complexos e edição por containers entra depois da revisão técnica.

## Princípios

1. **Não descartar o CanvasEditor atual.** O editor continua sendo o caminho de edição fina e compatibilidade.
2. **Não gerar HTML/CSS/JS livre.** A IA gera JSON declarativo dentro de schema controlado.
3. **Usar CSS/JS como capacidades do renderer, não como código arbitrário do modelo.** O modelo escolhe tokens, templates, layout e behaviors permitidos.
4. **Gerar beleza por código, preservar controle por layers.** O código cria composição profissional; `Layer[]` preserva edição.
5. **Começar com versão por código.** Só depois compilar para layers, exportar formatos complexos e editar containers.

## DesignDocument

Contrato inicial:

```ts
type HybridDesignPostContent = {
  kind: 'hybrid-design';
  version: 1;
  source: 'codegen';
  document: DesignDocument;
  pages?: DesignPage[];
};

type DesignDocument = {
  version: 1;
  format: 'single' | 'carousel' | 'story';
  width: number;
  height: number;
  tokens: DesignTokens;
  pages: DesignPageNode[];
};
```

`document` é a fonte rica da geração por código. `pages` é a versão compilada para o editor atual, quando existir.

## Tokens

Tokens devem ser explícitos para garantir consistência entre slides.

```ts
type DesignTokens = {
  colors: {
    background: string;
    surface: string;
    text: string;
    muted: string;
    accent: string;
    accent2?: string;
  };
  typography: {
    display: string;
    heading: string;
    body: string;
  };
  spacing: {
    page: number;
    section: number;
    gap: number;
  };
  radius: {
    sm: number;
    md: number;
    lg: number;
  };
  effects?: {
    shadow?: 'none' | 'soft' | 'premium' | 'dramatic';
    grain?: boolean;
    glass?: boolean;
    gradient?: boolean;
  };
};
```

## Nodes

A árvore deve ser semanticamente próxima de HTML/CSS, mas restrita.

```ts
type DesignPageNode = {
  id: string;
  type: 'page';
  name?: string;
  background: Paint;
  children: DesignNode[];
};

type DesignNode = ContainerNode | TextNode | ImageNode | ShapeNode;
```

### ContainerNode

```ts
type ContainerNode = {
  id: string;
  type: 'container';
  name?: string;
  role?: 'hero' | 'content' | 'footer' | 'card' | 'imageGroup' | 'decorativeGroup';
  layout: LayoutStyle;
  style?: VisualStyle;
  children: DesignNode[];
  editable?: {
    lockStructure?: boolean;
    allowUngroup?: boolean;
    allowChildrenEdit?: boolean;
  };
};
```

### LayoutStyle

```ts
type LayoutStyle = {
  position?: 'relative' | 'absolute';
  x?: number;
  y?: number;
  width?: number | string;
  height?: number | string;
  display?: 'block' | 'flex' | 'grid';
  direction?: 'row' | 'column';
  columns?: string[];
  rows?: string[];
  gap?: number;
  padding?: number | { top: number; right: number; bottom: number; left: number };
  alignItems?: 'start' | 'center' | 'end' | 'stretch';
  justifyContent?: 'start' | 'center' | 'end' | 'space-between';
};
```

### TextNode

```ts
type TextNode = {
  id: string;
  type: 'text';
  role?: 'eyebrow' | 'headline' | 'subtitle' | 'body' | 'caption' | 'cta';
  content: string;
  style?: TextStyle;
  layout?: LayoutStyle;
  behaviors?: Behavior[];
};
```

## CSS e JavaScript controlados

A IA não deve retornar CSS ou JS arbitrário. Ela pode escolher capacidades permitidas.

Exemplos de behaviors:

```ts
type Behavior =
  | { type: 'auto-fit-text'; min: number; max: number }
  | { type: 'balance-lines'; maxLines: number }
  | { type: 'smart-contrast' }
  | { type: 'image-focal-point'; x: number; y: number }
  | { type: 'equalize-card-heights' }
  | { type: 'stagger-children'; amount: number };
```

O renderer interpreta essas capacidades com código próprio, previsível e testável.

## Gemini pesado e contexto ampliado

A nova geração deve usar Gemini como cérebro de alta inteligência, não apenas como gerador de JSON de layers. O modelo recomendado para planejamento e DesignDocument é Gemini Pro/Thinking, com fallback para Flash apenas em etapas mecânicas.

### Camadas de contexto obrigatórias

1. **BrandConfig:** prompt do agente, guidelines, cores, fontes, logo.
2. **Referências analisadas:** insights de mercado, concorrentes, estilo visual e restrições.
3. **Histórico de decisões visuais da marca:** estilos aprovados/rejeitados, padrões recorrentes e preferências da Gabi.
4. **Objetivo da peça:** público, canal, CTA, densidade, formato, número de slides.
5. **Design brief estruturado:** copy, hierarquia, intenção emocional e promessa central.
6. **Regras de sistema visual:** tokens, templates permitidos, safe area, contraste, limites de densidade.
7. **Crítica interna:** checklist de qualidade antes de salvar.

### Orquestração proposta

```txt
Gemini Pro/Thinking
  1. interpreta briefing e contexto da marca
  2. escolhe direção visual e tokens
  3. escolhe templates por slide
  4. gera DesignDocument
  5. critica o próprio resultado contra checklist visual
  6. revisa se necessário

Gemini Flash
  - tarefas baratas e mecânicas
  - variações de copy
  - compactação de contexto
  - geração auxiliar de metadados
```

## Templates compiláveis

A primeira biblioteca deve ser pequena e forte. Candidatos MVP:

1. `premium-split-hero`
2. `bold-centered-statement`
3. `editorial-image-frame`
4. `stat-highlight`
5. `quote-testimonial`
6. `feature-grid`

A IA escolhe template e parâmetros. O código compila layout com qualidade previsível.

## Compatibilidade com o editor atual

O editor atual deve continuar consumindo `DesignPage[]` e `Layer[]`.

Função de extração recomendada:

```ts
function extractEditablePages(content: unknown): DesignPage[] | null {
  if (Array.isArray(content)) return content;
  if (isHybridDesign(content)) return content.pages ?? null;
  return null;
}
```

Com isso, posts antigos continuam abrindo. Posts novos podem começar como `hybrid-design` e só abrir no editor quando `pages` existir.

## Fases de implementação

### Fase 1 — Code Preview

- ✅ Criar schema `DesignDocument`.
- ✅ Criar `DesignDocumentRenderer` no frontend.
- 🔄 Criar endpoint experimental de geração por código.
- 🔄 Salvar post como `hybrid-design` com `document`.
- 🔄 Mostrar preview por código na Fábrica/Galeria.

### Fase 2 — Compiler para layers

- Criar `compileDesignDocumentToPages(document)`.
- Gerar `pages` compatíveis com `CanvasEditor`.
- Salvar `document + pages` no `Post.content`.
- Adaptar Galeria e Editor para reconhecer `hybrid-design`.

### Fase 3 — Edição containerizada

- Exibir árvore de nodes no editor.
- Selecionar container inteiro.
- Editar padding, gap, background, radius e layout.
- Permitir desagrupar container em layers.
- Permitir regenerar bloco específico com contexto local.

### Fase 4 — Outputs complexos

- Export PNG/JPEG primeiro.
- PDF depois.
- MP4/GIF apenas quando animação estiver madura.

## Checklist de revisão técnica antes da implementação

- Validar schema mínimo de `DesignDocument`.
- Decidir se o compiler roda no backend ou frontend; preferência inicial: backend para salvar post já compatível.
- Definir estratégia de versionamento (`version: 1`).
- Decidir storage de `document` e `pages` no mesmo `Post.content`.
- Definir limite de CSS/behaviors permitidos.
- Definir qual modelo Gemini será usado em cada etapa.
- Definir como compactar contexto da marca sem perder inteligência.
- Definir fallback se DesignDocument inválido.
- Definir métrica de qualidade visual comparando geração atual vs codegen.
- Validar que posts antigos continuam abrindo no editor.

## Decisões Tomadas

- A direção recomendada é híbrida: `DesignDocument` para geração por código, `Layer[]` para compatibilidade com o editor.
- CSS/JS devem ser recursos controlados do renderer, não código livre gerado pela IA.
- O primeiro objetivo é qualidade visual em preview por código. Edição containerizada e formatos complexos vêm depois.
- Gemini deve atuar como cérebro pesado com contexto ampliado na fase de planejamento, não apenas como gerador de layers.

## Learnings

- Design profissional depende mais de sistema visual, tokens e composição do que de coordenadas absolutas.
- Layers continuam úteis para edição fina, mas são um formato ruim para a IA desenhar do zero.
- Containers são a ponte natural entre design por código e editor visual.
- A solução reduz arrependimento porque preserva o CanvasEditor atual e cria um caminho incremental para qualidade superior.

## Relacionados

- [[designer-backend]]
- [[designer-frontend]]
- [[agente-designer]]
- [[render-layout-as-data]]
- [[agente-multimodelo]]
- [[adr-006-editor-visual-alternativas-canva]]
- [[fabrica-biblioteca-layouts]]
