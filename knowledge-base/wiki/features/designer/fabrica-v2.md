---
title: Fábrica v2 — Runtime Conversacional Híbrido
type: feature
tags:
  - "fabrica"
  - "chat"
  - "ai"
  - "designer"
  - "websocket"
  - "presentation-config"
status: active
created: 2026-04-27
updated: 2026-05-25
---

# 🏭 Fábrica v2 — Runtime Conversacional Híbrido

## Resumo

A Fábrica deixou de ser apenas um wizard procedural e passou a operar no runtime real como um **orquestrador conversacional híbrido**: chat ativo por WebSocket, perguntas estruturadas, contexto de marca persistido via `presentationConfig`, preview de design em tempo real e continuidade entre conversa, geração e galeria. Nesta iteração, o fluxo ficou mais próximo do padrão desejado para “acertar de primeira”, com menos fragilidade no contrato de perguntas, melhor reutilização de preferências visuais e interface de chat mais refinada.

**Nota de resultado desta iteração:** **8.7/10**.

## O que evoluiu nesta iteração

### 1. Contrato de perguntas estruturadas
- O runtime ativo deixou de depender apenas de parsing textual frágil de pergunta.
- A sessão agora carrega `activeQuestion` estruturada com:
  - `id`
  - `kind`
  - `question`
  - `options`
  - `allowFreeform`
  - `allowSkip`
  - `mode`
- O frontend passou a renderizar o accordion acima do composer com opções, campo livre e skip legítimo para modo automático.

### 2. `presentationConfig` como memória operacional da marca
- Preferências visuais passaram a ser persistidas e reinjetadas no runtime:
  - vibe visual
  - direção de paleta
  - paleta aprovada
  - ousadia
  - preferência por fotos
  - uso de SVG/layouts gráficos
  - modo automático padrão
- O brain já nasce com essas preferências no contexto, reduzindo perguntas desnecessárias.

### 3. Runtime conversacional real preservado
- O fluxo ativo permanece em `frontend/src/app/[marca]/fabrica/page.tsx` com `useFabricaWs`.
- O input continua sempre disponível.
- Durante streaming, mensagens do usuário entram automaticamente como `/btw` quando necessário, sem travar o composer.
- O caminho antigo paralelo (`FabricaChat/useBrainSession`) passou a servir mais como referência visual do que como fonte de verdade do runtime.

### 4. Regra de leitura reforçada
- Áreas com escrita passaram a tender para **superfície branca com texto preto**.
- A decisão deixou de ser apenas uma intenção de prompt: foi reforçada nos caminhos legado e híbrido para evitar drift visual em contraste de leitura.
- Paleta ousada continua permitida em áreas decorativas, imagens e composição geral.

### 5. Chat com mais acabamento visual
- Header, thread, bubbles, pills, progresso, accordion de perguntas e composer receberam polish visual.
- A leitura do chat ficou mais clara e mais coerente com o restante do frontend premium do projeto.
- O objetivo desta camada foi melhorar percepção sem reescrever a arquitetura do runtime.

## Arquitetura atual do fluxo

```text
Usuário conversa na Fábrica
  → sessão WebSocket ativa (`useFabricaWs`)
  → backend Brain mantém phase + reviewMode + activeQuestion + mensagens
  → contexto da marca + presentationConfig entram no brain
  → Brain responde / pergunta / despacha geração
  → pipeline híbrido produz DesignDocument/pages
  → preview aparece em tempo real
  → post salva histórico para reidratação posterior
```

## Arquivos relacionados
- Frontend runtime: `designer/frontend/src/app/[marca]/fabrica/page.tsx`
- Hook de sessão: `designer/frontend/src/hooks/useFabricaWs.ts`
- Sessão compartilhada: `designer/frontend/src/lib/fabricaSession.ts`
- Backend rota de sessão: `designer/backend/src/routes/fabrica.ts`
- Brain/orquestração: `designer/backend/src/agents/brain/index.ts`
- Contexto da marca: `designer/backend/src/lib/brandContext.ts`
- Persistência visual: `designer/backend/prisma/schema.prisma`

## Resultado percebido
- Menos drift entre pergunta, contexto e geração
- Menos dependência de convenções textuais frágeis
- Mais continuidade entre branding e execução
- Leitura visual mais previsível
- Chat do runtime real mais próximo do nível esperado para uso diário

## Próximos passos
- Fazer o `DesignDocument` assumir ainda mais do peso visual principal
- Aprofundar uso de fotos e composições mais sofisticadas
- Decidir melhor entre patch local e regeneração completa em correções
- Alinhar definitivamente o caminho paralelo legado com o runtime ativo

## Relacionados
- [[agente-designer]]
- [[designer-frontend]]
- [[design-document-hibrido]]
- [[design-document-compiler]]
- [[integracao-pipeline-hibrido]]
- [[fabrica-v2-plano]]
