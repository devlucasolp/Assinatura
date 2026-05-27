---
title: Galeria — Gestão de Ativos, Pastas e Histórico da Fábrica
type: feature	namespace: designer
tags:
  - "galeria"
  - "assets"
  - "drag-and-drop"
  - "management"
  - "fabrica"
  - "chat-history"
status: stable
sources:
  - "designer/frontend/src/app/[marca]/galeria/page.tsx"
  - "designer/frontend/src/app/[marca]/galeria/brand-galeria.module.css"
  - "designer/frontend/src/lib/designContent.ts"
  - "designer/frontend/src/app/[marca]/fabrica/page.tsx"
  - "designer/frontend/src/hooks/useFabricaWs.ts"
  - "designer/frontend/src/app/[marca]/editor/[postId]/page.tsx"
  - "designer/backend/src/agents/pipeline.ts"
created: 2026-04-27
updated: 2026-05-20
---

# 🎨 Galeria — Gestão de Ativos, Pastas e Histórico da Fábrica

A Galeria deixou de ser apenas um repositório de previews e passou a preservar contexto de geração. Além de organizar artes em pastas e permitir exclusão rápida, agora ela consegue abrir apresentações salvas pela Fábrica, mostrar o histórico da conversa que gerou cada peça e reabrir a sessão correspondente no chat quando houver `sessionId` persistido.

## Resumo

A melhoria de 2026-05-20 resolveu duas dores práticas do fluxo do Designer:
- visualizar melhor os designs gerados na galeria, inclusive apresentações multi-slide;
- recuperar o histórico da conversa da Fábrica que levou àquela arte.

Para isso, o pipeline passou a salvar um envelope de conteúdo `fabrica-design` com `pages`, `sessionId` e `chatHistory`. O frontend da galeria interpreta esse envelope sem quebrar compatibilidade com posts antigos salvos como `DesignPage[]` puro.

## 🖱️ Drag-and-Drop (DND)
Implementamos um sistema de arrastar e soltar para organização de artes:
- **Origem**: Cards de artes (`postCard`).
- **Destino**: Pastas (`folderCard`).
- **Feedback**: As pastas mudam de cor (`folderCardDragOver`) ao receber um item.
- **Restrições**:
    - Não é permitido drop em "Todas as Artes" (filtro global).
    - Não é permitido drop na mesma pasta onde o item já reside.
    - Drop em "Sem Pasta" move o item para `folderId: null`.

## 👁️ Visualização de designs na galeria
A galeria agora trata três cenários distintos de preview:
- **imagem simples**: abre modal de imagem e download;
- **design em páginas**: renderiza thumbnail do primeiro slide com `DesignRenderer` e abre modal de apresentação completa;
- **DesignDocument híbrido não compilado**: sinaliza preview pendente sem abrir canvas vazio.

Isso depende dos helpers de parsing em `designContent.ts`, que identificam se o conteúdo salvo é:
- `DesignPage[]` legado;
- `hybrid-design`;
- `fabrica-design`;
- ou payload simples de imagem.

## 💬 Histórico da conversa da Fábrica
Cada post novo gerado pela Fábrica pode carregar:
- `sessionId`;
- `chatHistory[]` com mensagens `user`, `assistant` e `system`;
- `pages` do design final.

Na galeria:
- cards em grade e lista exibem ação **Ver conversa** quando existe histórico ou sessão associada;
- o modal mostra a thread cronológica com papel, timestamp e conteúdo integral;
- quando existe `sessionId`, aparece link para reabrir a sessão da Fábrica.

## 🔁 Reabertura da sessão no chat
A página `/{marca}/fabrica` passou a aceitar `?sessionId=...`.

Com isso, a galeria consegue não só mostrar o histórico estático salvo no post, mas também tentar reidratar a sessão viva da Fábrica via WebSocket + `GET /api/fabrica/sessions/:sessionId`, recuperando mensagens, design atual e estado da revisão quando a sessão ainda existe no Redis.

## ✏️ Compatibilidade com o Editor
O editor visual foi ajustado para não destruir esse envelope ao salvar:
- se o post for `hybrid-design`, preserva `document` e atualiza `pages`;
- se o post for `fabrica-design`, preserva `sessionId` e `chatHistory` e atualiza apenas `pages`.

Isso evita perder o histórico depois de uma edição manual posterior na peça.

## 🗑️ Gestão de Exclusão
Adicionamos suporte completo para limpeza de ativos:
- **Artes**: Botão de exclusão rápida no card e no modal de preview. Aciona `DELETE /api/posts/:id`.
- **Pastas**: Botão de exclusão na lista de pastas.
- **UX**: Confirmação via `confirm()` antes de ações destrutivas.

## 🔄 Sincronização de Estado
Uso do padrão de **Mutação SWR-like** (via `mutate` no `useBrandPosts`):
- As ações de mover e excluir atualizam a UI instantaneamente sem reload da página.
- O preview em tela cheia é fechado automaticamente se a arte for excluída.
- O modal de conversa opera diretamente sobre o conteúdo salvo no post, sem depender de nova ida ao backend.

## 🛠️ API & Backend
Implementações relevantes para essa etapa:
- `DELETE /api/posts/:id`: remoção física do registro no Prisma.
- `PUT /api/posts/:id`: suporte a troca de `folderId` e preservação do envelope ao editar.
- `POST /api/fabrica/sessions`: criação da sessão.
- `GET /api/fabrica/sessions/:sessionId`: reidratação de sessão para reconexão.
- `runPipeline()`: persistência do conteúdo como `fabrica-design` com `pages`, `sessionId` e `chatHistory`.

## Decisões tomadas
- O histórico foi salvo dentro de `Post.content`, não em novo schema relacional, para evitar migração de banco neste momento.
- O envelope `fabrica-design` foi adotado como compat layer: posts antigos continuam abrindo, e posts novos ganham contexto adicional.
- A galeria mostra o histórico salvo localmente no post e usa `sessionId` apenas como caminho complementar para reabrir o fluxo na Fábrica.

## Learnings
- O problema do usuário não era só “preview ruim”; era perda de contexto entre geração e consulta posterior.
- Preservar `sessionId` sem preservar também `chatHistory` seria insuficiente, porque a sessão em Redis expira.
- Preservar `chatHistory` sem adaptar o editor quebraria a utilidade da feature após qualquer edição manual.

## 📁 Arquivos Relacionados
- Frontend: `src/app/[marca]/galeria/page.tsx`, `src/app/[marca]/galeria/brand-galeria.module.css`
- Frontend: `src/lib/designContent.ts`, `src/app/[marca]/fabrica/page.tsx`, `src/hooks/useFabricaWs.ts`
- Frontend: `src/app/[marca]/editor/[postId]/page.tsx`
- Backend: `src/agents/pipeline.ts`, `src/routes/posts.ts`, `src/routes/fabrica.ts`
- Hooks: `src/lib/hooks.ts`

## Relacionados
- [[fabrica-v2]] — fluxo de criação que origina os posts da galeria
- [[designer-frontend]] — rotas, hooks e composição visual do Designer
- [[designer-backend]] — persistência de sessão e pipeline da Fábrica

## ✅ Status
- [x] Drag-and-Drop de arquivos para pastas
- [x] Exclusão de artes (Frontend + Backend)
- [x] Atualização de UI sem reload
- [x] Prevenção de drops redundantes
- [x] Visualização de apresentações multi-slide na galeria
- [x] Persistência de `sessionId` + `chatHistory` nos posts da Fábrica
- [x] Modal de histórico da conversa por arte
- [x] Reabertura da sessão da Fábrica via query string
- [x] Preservação do envelope no Editor visual
