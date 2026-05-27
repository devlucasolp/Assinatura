# Arquitetura do Designer — Estrutura Atual e Proposta de Modularização

## Contexto
Data: 2026-05-24  
Objetivo: organizar o Designer para suportar múltiplos formatos (apresentação, Instagram, animação) sem downgrade na geração atual.

---

## 1. Estrutura Atual (Estado em 2026-05-24)

### Backend (`designer/backend/src/`)

#### Pastas Principais
```
src/
├── agents/
│   ├── brain/           # Cérebro conversacional (Fábrica)
│   ├── planner/         # Planejador de estrutura/narrativa
│   ├── content/         # Gerador de texto por slide
│   ├── design/          # Montador de layers (template + conteúdo)
│   ├── image/           # Seletor/gerador de imagens
│   ├── reviewer/        # Revisor do resultado final
│   ├── tools/           # Ferramentas do Brain (set_design)
│   ├── worker/          # Worker em background
│   ├── pipeline.ts      # Pipeline LEGADO (Fábrica v2)
│   └── types.ts
├── lib/
│   ├── templates/       # Templates de layout (presentation, carousel)
│   ├── designDocument/  # (no frontend) — no backend temos o type+validator
│   ├── designDocument.ts
│   ├── fabricaLegacy.ts # Utilitários para pipeline legado
│   ├── nanoBanana.ts    # Motor de design visual (Nano Banana)
│   ├── designFixer.ts   # Revisor de design existente
│   ├── fixJobStore.ts
│   ├── geminiRetry.ts
│   ├── imageNormalizer.ts
│   ├── prisma.ts
│   ├── redis.ts
│   └── websocket.ts
├── middleware/
│   ├── auth.ts
│   ├── errorHandler.ts
│   └── requestLogger.ts
└── routes/
    ├── ai.ts            # MONOLÍTICO (2437 linhas!)
    ├── fabrica.ts
    ├── brands.ts
    ├── posts.ts
    ├── folders.ts
    ├── settings.ts
    ├── upload.ts
    └── ...
```

#### Pontos Fortes
- **Agentes separados por responsabilidade**: planner/content/design/image/reviewer
- **DesignDocument híbrido** como camada de abstração semântica
- **Compiler frontend** para materializar DesignDocument em layers
- **Brain + Worker** separados para conversação e execução em background

#### Pontos de Acoplamento Alto
1. **`routes/ai.ts` muito grande**:
   - `generate-design-document`
   - `generate-design` (SSE)
   - `create` (SSE)
   - `create-job` (background)
   - `fix-design-job`
   - etc.
2. **Código repetido** em prompts e validações
3. **Pipeline legado** vs **DesignDocument híbrido** são caminhos separados sem muita abstração comum
4. **Templates** são específicos para presentation/carousel; sem abstração para formatos diferentes (Instagram, animação)

---

### Frontend (`designer/frontend/src/`)

#### Pastas Principais
```
src/
├── app/[marca]/
│   ├── fabrica/         # Chat + preview (Fábrica)
│   ├── galeria/         # Galeria da marca
│   ├── editor/          # CanvasEditor próprio
│   └── configuracoes/
├── components/
│   ├── DesignDocument/
│   │   ├── DesignDocumentRenderer.tsx
│   │   └── fixtures.ts
│   ├── Editor/          # CanvasEditor + painéis
│   ├── Fabrica/         # Components da Fábrica
│   ├── FabricaChat/     # Chat do Brain
│   ├── Sidebar/
│   └── ui/              # Componentes compartilhados
├── hooks/
│   ├── useFabricaWs.ts
│   ├── useBrainSession.ts
│   └── useDesignFixer.ts
└── lib/
    ├── designContent.ts
    ├── designDocument/    # Compiler + guards + styles + types (abstração frontend)
    ├── api.ts
    └── ...
```

#### Pontos Fortes
- **`lib/designDocument/`** bem organizada no frontend
- **Editor modular** por painéis (TextPanel, ImagePanel, etc.)
- **`useFabricaWs` + `useBrainSession`** separados

---

## 2. Proposta de Estrutura Modular (Sem Downgrade)

Princípios:
1. **Manter a geração atual intocada** (não mexer no pipeline legado ainda)
2. **Abstrair formatos em `engines/`** (uma engine por formato)
3. **Quebrar `routes/ai.ts` em módulos**
4. **Unificar interfaces comuns** entre formatos

---

### Passo 1 — Refatorar Backend: Quebrar `routes/ai.ts`

#### Nova Estrutura Proposta para Backend
```
src/
├── agents/
│   ├── brain/
│   ├── planner/
│   ├── content/
│   ├── design/
│   ├── image/
│   ├── reviewer/
│   ├── tools/
│   ├── worker/
│   ├── pipeline.ts      # Pipeline LEGADO (mantido)
│   └── types.ts
├── lib/
│   ├── templates/
│   │   ├── presentation/
│   │   ├── carousel/
│   │   ├── instagram/     # (futuro)
│   │   └── types.ts
│   ├── designDocument.ts
│   ├── fabricaLegacy.ts
│   ├── nanoBanana.ts
│   ├── designFixer.ts
│   ├── geminiRetry.ts
│   ├── imageNormalizer.ts
│   ├── prisma.ts
│   ├── redis.ts
│   └── websocket.ts
├── engines/
│   ├── presentation/      # Engine para apresentação
│   │   ├── index.ts
│   │   ├── pipeline.ts
│   │   ├── templates.ts
│   │   └── types.ts
│   ├── hybrid/           # Engine para DesignDocument híbrido
│   │   ├── index.ts
│   │   ├── generate.ts
│   │   └── validate.ts
│   └── instagram/        # (futuro)
├── routes/
│   ├── ai/
│   │   ├── design-document.ts  # generate-design-document
│   │   ├── create-job.ts       # create-job (background)
│   │   ├── create.ts           # create (SSE)
│   │   ├── fix-design-job.ts   # fix-design-job
│   │   └── index.ts            # Router que agrupa tudo
│   ├── fabrica.ts
│   ├── brands.ts
│   └── ...
├── middleware/
└── app.ts
```

---

### Passo 2 — Interfaces Comuns

Definir interfaces comuns para engines, para que a API e o frontend não dependam de implementações específicas:

```typescript
// src/engines/types.ts
export interface DesignEngine {
  name: string;
  supports(format: DesignFormat): boolean;
  generate(params: EngineParams): Promise<EngineResult>;
}

export interface EngineParams {
  prompt: string;
  brandSlug: string;
  format: DesignFormat;
  width?: number;
  height?: number;
  slideCount?: number;
  templates?: string[];
  projectAssets?: Asset[];
  referenceAsset?: Asset;
  userId?: string;
}

export interface EngineResult {
  kind: 'legacy' | 'hybrid';
  pages?: unknown[];
  document?: DesignDocument;
  postId?: string;
}
```

---

### Passo 3 — Quebrar `routes/ai.ts`

1. Extrair cada endpoint em seu próprio arquivo dentro de `routes/ai/`
2. Usar `ai/index.ts` para agrupar os routers

Exemplo:
```typescript
// src/routes/ai/design-document.ts
import { Router } from 'express';
import { generateDesignDocument } from '../../lib/designDocument.js';

export const designDocumentRouter = Router();
designDocumentRouter.post('/:slug/generate-design-document', async (req, res, next) => {
  // lógica aqui
});
```

---

### Passo 4 — Engines Específicas (Sem Mexer no Legado)

1. **Engine `hybrid/`**:
   - Responsável por `DesignDocument`
   - Usa `generateDesignDocument()` + `reviewDesignDocument()`
   - Joga para compiler frontend quando necessário

2. **Engine `presentation/`**:
   - Pipeline legado, mantido como está
   - Não modificar por agora, só mover para pasta organizada

3. **Engine `instagram/` (futuro)**:
   - Dimensões específicas (1:1, 9:16, etc.)
   - Templates próprios
   - Pesquisa de referências específicas para Instagram

---

### Passo 5 — Frontend: Abstrair Formatos

No frontend, manter a estrutura, mas:
- `lib/designDocument/` continua como está
- Adicionar `lib/engines/` se precisar (provavelmente não, pois a API abstrai)
- Manter `useFabricaWs` e `useBrainSession`

---

## 3. Plano de Evolução (Sem Downgrade)

| Etapa | Ação | Risco | Impacto |
|-------|------|-------|---------|
| 1 | Quebrar `routes/ai.ts` em módulos em `routes/ai/` | Baixo | Organização melhor |
| 2 | Mover pipeline legado para `engines/presentation/` | Baixo | Preparar para outros formatos |
| 3 | Criar `engines/hybrid/` com lógica do híbrido | Médio | Isolar híbrido |
| 4 | Definir interfaces comuns `DesignEngine` | Médio | Abstração para formatos |
| 5 | Criar `engines/instagram/` (esqueleto vazio) | Baixo | Preparar para futuro |

---

## 4. Principais Vantagens

✅ **Geração atual intocada**: não mexemos no pipeline legado por enquanto  
✅ **Organização melhor**: `routes/ai.ts` quebrado em arquivos menores  
✅ **Evolução segura**: adicionamos engines novos sem quebrar o existente  
✅ **Reutilização**: interfaces comuns permitem reutilizar validações/utilitários  
✅ **Caminho claro para Instagram/animação**: basta criar uma nova engine

