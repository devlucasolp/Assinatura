---
title: "Timeline Calendário Obsidian — Projeto Assinatura"
type: output
tags:
  - "timeline"
  - "calendario"
  - "obsidian"
  - "execucao"
  - "gabi"
  - "designer"
  - "marcelle"
sources:
  - "wiki/log.md"
  - "wiki/outputs/calendario-notion-execucao-2026-04-01-2026-05-13.md"
  - "wiki/outputs/relatorio-entregas-valor-agregado-2026-05-14.md"
  - "wiki/outputs/revisao-contratual-escopo-cronograma-aceite-2026-05-14.md"
created: 2026-05-14
updated: 2026-05-14
---

# Timeline Calendário Obsidian — Projeto Assinatura

## Como usar

> Nota de alinhamento: para leitura contratual/financeira e critérios de aceite, use esta timeline junto com [[revisao-contratual-escopo-cronograma-aceite-2026-05-14]].

Esta página foi pensada para leitura em Obsidian. Cada semana tem:

- intervalo de datas;
- entregas principais;
- classificação contratual;
- checklist de itens/subitens;
- links internos para evidência na KB.

Legenda:

- Entregue
- Em validação/teste
- Pendente/futuro
- Entrega adicional
- Adiantamento de escopo contratado
- Contratado
- Infraestrutura/governança

## Visão mensal rápida

### Abril 2026

| Semana | Período | Foco | Resultado |
|---|---|---|---|
| Semana 1 | 01/04–06/04 | Preparação operacional | Contrato ativo; execução inicial sem granularidade completa na KB |
| Semana 2 | 07/04–13/04 | Bot Gabi MVP 1/2 | MVP 1 + MVP 2 implementados; features bônus do bot já aparecem |
| Semana 3 | 14/04–20/04 | Fundação Designer | Base Next.js + Express + Prisma + Fábrica/Galeria/Editor inicial |
| Semana 4 | 21/04–27/04 | KB, Sprint 0, Fábrica v2, Galeria | Designer vira MVP técnico navegável; KB canônica criada |

### Maio 2026

| Semana | Período | Foco | Resultado |
|---|---|---|---|
| Semana 5 | 28/04–04/05 | Consolidação e ADRs | Contrato Marcelle corrigido; ADRs; benchmarking; biblioteca layouts |
| Semana 6 | 05/05–11/05 | Decisão editor próprio | Canva sai do caminho principal; CanvasEditor próprio reativado |
| Semana 7 | 12/05–14/05 | Editor avançado, jobs, qualidade | Multi-select, revisão IA, jobs recuperáveis, contraste, rotas, upload/R2 |

---

# Abril 2026

## Semana 1 — Preparação operacional inicial

**Período:** 2026-04-01 a 2026-04-06  
**Áreas:** Gabi, Marcelle, Designer  
**Status:** Base contratual / histórico parcial  
**Evidências:** [[escopo-projeto-assinatura]], [[secretaria-ai-gabi]], [[automacao-notificacao-marcelle]]

### Entregas e contexto

- Contrato ativo desde 24/03/2026.
- Projeto estruturado em duas frentes paralelas:
  - Secretária A.I. + Designer Gabi.
  - Automação de Notificação Marcelle.
- Prazo contratual de 4 meses para ambas as frentes.
- Execução registrada com granularidade mais forte a partir dos commits do Bot Gabi e da KB canônica.

### Classificação

- Contratado: organização inicial e execução das frentes.
- Governança: separação posterior entre Gabi, Marcelle, Designer e infraestrutura compartilhada.

---

## Semana 2 — Bot Gabi MVP 1/2 implementado

**Período:** 2026-04-07 a 2026-04-13  
**Áreas:** Gabi, WhatsApp, Asana, IA, Infraestrutura  
**Status:** Entregue / adiantado / features bônus no bot  
**Evidências:** [[bot-gabi]], [[secretaria-ai-gabi]]

### Entregas contratadas

- MVP 1 — mensagens automáticas durante reunião/evento.
- MVP 2 — atas de reunião publicadas no Asana.
- MVP 2 entregue junto do MVP 1, antes da janela contratual do Mês 2.

### Subitens do MVP 1

- Auto-reply por status de reunião/evento.
- Estado salvo em Redis.
- Mensagens configuráveis por ambiente.
- Controle para não repetir resposta para o mesmo contato.

### Subitens do MVP 2

- Comandos `/ata`, `processar ata`, `subir ata`.
- Gemini estrutura ata.
- Publicação no Asana.
- Salvamento em PostgreSQL.
- Confirmação com link.

### Features bônus Gabi Bot

- CRUD Asana via WhatsApp:
  - criar tarefa;
  - atualizar tarefa;
  - concluir tarefa;
  - deletar tarefa;
  - buscar tarefa;
  - retornar link da última tarefa.
- Processamento de áudio:
  - transcrição/interpretação com IA;
  - entrada no fluxo normal do bot.
- Processamento de imagem:
  - descrição/interpretação com Gemini;
  - uso como texto operacional.
- Debounce inteligente:
  - agrupa rajadas de mensagens;
  - reduz custo;
  - melhora contexto.
- Estado pendente multi-turno:
  - confirmações;
  - continuidade de fluxo;
  - respostas curtas não caem no chat geral.
- Anti-loop:
  - ignora `fromMe`;
  - evita bot responder a si mesmo.
- Estratégia dual LLM:
  - Gemini para extração/atas/mídia;
  - GPT-4o para chat/classificação.
- Histórico conversacional em PostgreSQL.

### Observação executiva

Esta semana é o primeiro marco forte de valor agregado: as entregas contratadas foram feitas cedo e o bot já nasceu com capacidade operacional maior que a prevista para auto-reply + atas.

---

## Semana 3 — Fundação do Designer IA

**Período:** 2026-04-14 a 2026-04-20  
**Áreas:** Designer, Gabi, Produto  
**Status:** Entregue / fase contratada adiantada  
**Evidências:** [[agente-designer]], [[designer-backend]], [[designer-frontend]]

### Entregas

- Base frontend Next.js.
- Base backend Express.
- Prisma/PostgreSQL.
- Rotas iniciais:
  - auth;
  - settings;
  - posts;
  - AI.
- Estrutura por marca com slug.
- Configuração de marca:
  - guidelines;
  - prompt do agente;
  - cores;
  - fontes.
- Base inicial para:
  - Fábrica;
  - Galeria;
  - Editor visual.

### Classificação

- Gerador de imagens/apresentações era contratado.
- Fundação iniciada antes da janela formal do Mês 3.
- Profundidade técnica inicial acima do mínimo de “gerador simples”.

---

## Semana 4 — KB canônica, Sprint 0, qualidade, Fábrica v2 e Galeria

**Período:** 2026-04-21 a 2026-04-27  
**Áreas:** Designer, Gabi, Marcelle, KB, Produto  
**Status:** Entregue / valor agregado em governança e produto  
**Evidências:** [[log]], [[fabrica-v2]], [[galeria-gestao]], [[qualidade-lint-build]], [[designer-plano-implementacao]], [[auditoria-ux-logica-designer]]

### 2026-04-22 — KB canônica

- KB inicializada.
- Ingestão de escopo.
- Ingestão Gabi.
- Ingestão Marcelle.
- Ingestão Bot Gabi.
- Ingestão Designer.
- Estrutura de wiki:
  - index;
  - log;
  - overview;
  - features;
  - architecture;
  - decisions;
  - outputs.

### 2026-04-24 — Pesquisa e auditorias

- Pesquisa de geração de imagem/PDF.
- Auditoria de jornada do Designer.
- Plano de implementação.
- Auditoria de libs/configs.
- Priorização de gaps.

### 2026-04-25 — Sprint 0 Designer

- SDK `@google/genai`.
- Gemini 2.5.
- Endpoint de geração de imagem.
- Correções de env/API.
- Revisão de configurações de marca.
- Auditoria UX/lógica.

### 2026-04-27 — Fábrica v2 e Galeria

- Fábrica v2 com wizard.
- Preview responsivo.
- Gestão de assets.
- Galeria com:
  - grid/list view;
  - pastas;
  - drag-and-drop;
  - exclusão;
  - preview modal.
- Lint/build limpos.

### Classificação

- Designer era contratado.
- Galeria operacional e governança KB são valor agregado de produto/projeto.
- Auditorias e lint/build recorrentes são valor agregado de qualidade.

---

# Maio 2026

## Semana 5 — Consolidação, ADRs estruturais e evolução da Fábrica

**Período:** 2026-04-28 a 2026-05-04  
**Áreas:** Designer, Gabi, Marcelle, Infraestrutura, Produto  
**Status:** Entregue / valor agregado em governança técnica  
**Evidências:** [[adr-001-next-express-separados]], [[adr-002-gemini-llm-designer]], [[adr-003-infra-compartilhada]], [[benchmarking-fabrica-ux]], [[fabrica-biblioteca-layouts]], [[stripe-webhook]]

### Entregas

- Sanitização e consolidação da KB.
- Correção do contrato Marcelle para 4 meses paralelos.
- ADR-001 — Next.js + Express separados.
- ADR-002 — Gemini como LLM principal do Designer.
- ADR-003 — infraestrutura compartilhada Gabi/Marcelle.
- Stripe webhook documentado.
- Benchmarking UX:
  - Canva;
  - Gamma;
  - Beautiful.ai;
  - Pitch/Slidebean.
- Biblioteca de layouts da Fábrica.
- Fluxo central da Secretária A.I. documentado.

### Classificação

- ADRs e benchmarking são valor agregado de governança/produto.
- Infra compartilhada reduz custo futuro da Marcelle.
- Marcelle segue contratada, mas a base foi reposicionada e documentada com mais clareza.

---

## Semana 6 — ADR-005/ADR-006 e retorno do CanvasEditor próprio

**Período:** 2026-05-05 a 2026-05-11  
**Áreas:** Designer, Editor, IA visual, Infraestrutura  
**Status:** Entregue / valor agregado no Designer  
**Evidências:** [[adr-005-canva-api-migração]], [[canva-connect-api]], [[adr-006-editor-visual-alternativas-canva]], [[designer-backend]], [[designer-frontend]], [[agente-designer]]

### 2026-05-05 — Canva avaliado

- ADR-005 aceita temporariamente.
- Canva Connect API documentada.
- OAuth, assets, autofill e export avaliados.

### 2026-05-06 — Alternativas reavaliadas

- Bloqueios de Canva iframe identificados.
- Penpot avaliado e adiado por RAM.
- Fabric.js preterido pelo custo de reconstrução.
- Mapa visual de agentes criado.

### 2026-05-11 — CanvasEditor próprio reativado

- ADR-006 aceita.
- CanvasEditor próprio volta ao caminho principal.
- `react-rnd` com escala.
- ResizeObserver.
- Sidebar de camadas.
- Painéis por layer.
- Correções de null/crash.
- Pipeline 3 passos:
  - brief/roteiro;
  - text layers;
  - Nano Banana visual.
- `geminiRetry`.
- `imageNormalizer`.
- Fallbacks de geração.
- Folder model.
- Rotas folders/upload.

### Classificação

- Gerador visual era contratado.
- Editor visual próprio é profundidade acima do mínimo.
- Avaliação técnica de alternativas e ADRs é valor agregado de arquitetura.

---

## Semana 7 — Editor avançado, revisão IA, jobs e qualidade visual

**Período:** 2026-05-12 a 2026-05-14  
**Áreas:** Designer, Gabi, Marcelle, KB, Qualidade  
**Status:** Entregue / indo para teste / valor agregado forte  
**Evidências:** [[designer-frontend]], [[designer-backend]], [[agente-designer]], [[auditoria-geral-designer-2026-05-13]], [[relatorio-entregas-valor-agregado-2026-05-14]]

### 2026-05-12 — Editor multi-select e pipeline robusto

- Multi-select no editor.
- Ctrl+click no canvas/sidebar.
- Marquee selection.
- Multi-drag.
- Alinhamento em lote.
- Distribuição horizontal/vertical.
- Atalhos em massa.
- Auditoria/correções da Fábrica:
  - text zones estruturadas;
  - clamp de layers;
  - prompt decisivo;
  - cálculo real de altura de texto;
  - consistência visual.

### 2026-05-13 — Animação, timeline, auditoria e imagens contextuais

- Preview de animação no canvas.
- Persistência de abas.
- Limpeza de dead code.
- Timeline do Designer.
- Status Gabi/Marcelle atualizado.
- Auditoria geral do Designer.
- Imagens contextuais por slide:
  - botão “IA nos slides”;
  - roteiro primeiro;
  - zonas de texto;
  - imagem contextual por slide;
  - logo como identidade visual.
- Regra global de contraste:
  - texto branco em fundo escuro;
  - texto preto em fundo claro;
  - box translúcido sobre imagem/foto/gradiente.
- Edição em lote de textos.

### 2026-05-14 — Jobs, rotas e upload/R2

- Auditoria de criação assíncrona e revisão.
- `create-job`.
- `jobs/:jobId`.
- `jobs/:jobId/stream`.
- `fix-design-job`.
- `fix-jobs/:jobId`.
- `fix-jobs/:jobId/stream`.
- `fix-jobs/:jobId/input`.
- Slug bruto nas chamadas API.
- Rotas top-level reservadas protegidas:
  - equipe;
  - extras;
  - galeria;
  - login;
  - onboarding.
- Upload/R2 com validação clara.

### Features bônus Designer nesta semana

- Multi-select avançado.
- Edição em lote de textos.
- Revisão IA com aprovação humana.
- Jobs recuperáveis.
- Regra global de contraste.
- Imagens contextuais por slide.
- Upload/R2 com erros claros.
- Correções de rotas e slug para reduzir erro operacional.

### Classificação

- Designer/Gerador era contratado.
- Profundidade do editor, revisão IA, jobs e qualidade visual são valor agregado.
- Estado final: pronto para validação real com Gabi, com Drive ainda pendente no ecossistema.

---

# Visão por frente

## Gabi — contratado

- MVP 1 — mensagens automáticas.
- MVP 2 — atas no Asana.
- MVP 3 — gerador de imagens/apresentações em teste.
- MVP 4 — validação e lançamento.

## Gabi — adiantado

- MVP 2 entregue junto do MVP 1.
- Designer iniciado antes do Mês 3.
- Designer praticamente pronto para testes antes de 20/05.

## Gabi — features bônus reais

- CRUD Asana via WhatsApp.
- Áudio no WhatsApp.
- Imagem no WhatsApp.
- Debounce inteligente.
- Estado pendente multi-turno.
- Anti-loop.
- Controle de repetição no auto-reply.
- Dual LLM.
- Histórico conversacional.
- Degradação graceful.

## Designer Gabi — bônus/profundidade acima do mínimo

- Editor visual próprio.
- Galeria com pastas/DND.
- Multi-select.
- Edição em lote.
- Revisão IA.
- Jobs recuperáveis.
- Contraste global.
- Imagens contextuais por slide.

## Marcelle

- Mês 1 entregue.
- Mês 2 indo para teste operacional.
- Infra reaproveitada da Gabi.
- Dashboard unificado segue fora do escopo.

## Projeto/Governança

- KB viva.
- ADRs.
- Auditorias.
- Benchmarking.
- Calendário Notion.
- Timeline Obsidian.

---

# Pendências reais

- [ ] Validação real com Gabi.
- [ ] Integração Google Drive no ecossistema Gabi.
- [ ] Teste operacional Marcelle na semana de 18/05/2026.
- [ ] Decisão final de UX da Fábrica depois do teste.
- [ ] Persistência de jobs em banco se houver requisito de retomada pós-restart.

## Relacionados

- [[relatorio-entregas-valor-agregado-2026-05-14]]
- [[calendario-notion-execucao-2026-04-01-2026-05-13]]
- [[secretaria-ai-gabi]]
- [[bot-gabi]]
- [[agente-designer]]
- [[automacao-notificacao-marcelle]]
- [[overview]]
- [[revisao-contratual-escopo-cronograma-aceite-2026-05-14]]
