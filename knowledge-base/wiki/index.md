---
title: Index â€” CatÃ¡logo Master da Wiki
type: architecture
tags:
  - "index"
  - "toc"
sources: []
created: 2026-04-22
updated: 2026-05-15
---

# ðŸ—‚ï¸ Index â€” CatÃ¡logo Master

> Toda pÃ¡gina nova da wiki DEVE ser registrada aqui na seÃ§Ã£o correspondente.
> O `/memory-query` usa este arquivo como ponto de partida para localizar conteÃºdo.

## ðŸ›ï¸ Architecture

- [[designer-backend]] — Express + Prisma + PostgreSQL + Gemini; rotas, auth middleware, nanoBanana engine e upload R2 validado
- [[designer-frontend]] — Next.js App Router, [marca] dynamic routes, Fábrica (chat/SSE), CanvasEditor
- [[agente-multimodelo]] — Proposta histórica LLM + tools; Vercel AI SDK não foi implementado; evolução recomenda Gemini pesado + DesignDocument
- [[render-layout-as-data]] — JSON layers/DesignDocument → render determinístico; layers seguem como formato compilado/editável
- [[design-document-hibrido]] — Proposta de geração por código seguro: Gemini pesado + contexto ampliado → DesignDocument React/CSS → Layer[] compatível com CanvasEditor

## ✨ Features

- [[integracao-pipeline-hibrido]] — Integração urgente do pipeline híbrido (Fábrica salva document, frontend compila, fallback legado).
- [[bot-gabi]] — FastAPI+Python; MVP 1 ✅ (auto-reply) e MVP 2 ✅ (atas→Asana) implementados; deploy EasyPanel
- [[agente-designer]] — App Next.js+Express de geração de designs via Nano Banana (Gemini JSON mode); Pipeline híbrido validado 🔄
- [[fabrica-v2]] — Runtime conversacional híbrido da Fábrica: WebSocket, perguntas estruturadas, `presentationConfig`, preview em tempo real e nota 8.7 na iteração de 2026-05-25.
- [[fabrica-v2-plano]] — Novo plano de implementação arquitetural da Fábrica v2 Híbrida Modular (2026-05-24)
- [[fabrica-redesign]] — Histórico; proposta substituída pelo modelo híbrido conversacional (Fábrica v2).
- [[fabrica-biblioteca-layouts]] — 6 layouts MVP, layoutKey canônico, metadados, benchmarking de modelos
- [[galeria-gestao]] — Gestão e visualização da Galeria de Artes, agora suportando reidratação de sessões e chatHistory por arte (atualizado 2026-05-24).
- [[design-document-renderer]] — Tipagem estrita e componente de preview seguro para DesignDocument (Code Preview)
- [[design-document-compiler]] — Compilação segura DesignDocument → DesignPage[] para Editor/Galeria compatíveis com CanvasEditor
- [[secretaria-ai-gabi]] — Agente WhatsApp + atas + gerador de imagens; bot partindo para testes; Drive pendente; execução adiantada (2026-05-13)
- [[secretaria-ai-mes2]] — Semanas 5–8 | deadline 19/05/2026 | histórico; status atual avançou para testes
- [[automacao-notificacao-marcelle]] — 4 meses paralelos, R$ 1.000/mês × 10 | Mês 1 ✅ | Mês 2 🔄 teste operacional semana 18/05/2026

## 🔌 Integrations

- [[infraestrutura-tecnica]] — Asana API ✅ + WhatsApp/Evolution API ✅ + EasyPanel + Gemini + ChatGPT
- [[stripe-webhook]] — Webhook ✅ | Facebook CAPI ⚠️ | TikTok CAPI ⚠️ | UTM ❌ (não implementado)
- [[canva-connect-api]] — Histórico/stand-by pós-ADR-006; não é o caminho principal do editor embarcado

## ðŸ” Security

_Nenhuma pÃ¡gina ainda. Criar: JWT httpOnly vs localStorage (ADR pendente)._

## 🔄 Workflows

- [[escopo-projeto-assinatura]] — Contrato Lucas × Assinatura Ltda; dois produtos paralelos (Gabi 4m + Marcelle 4m)
- [[qualidade-lint-build]] — Lint e build limpos no frontend e backend (2026-04-27)
- [[bot-01-backend-gemini-designdocument]] — ✅ Concluído: tipagens, validações defensivas e endpoint experimental de geração do DesignDocument usando Gemini Pro
- [[bot-02-frontend-renderer-designdocument]] — ✅ Concluído: renderer seguro frontend isolado, tipagens correspondentes e preview visual por código
- [[bot-03-compat-editor-auditoria-designdocument]] — ✅ Concluído: helpers de compatibilidade, extração segura, auditoria e testes contra falsos positivos para o DesignDocument
- [[designer-timeline-execucao]] — Timeline do Designer atualizada com DesignDocument híbrido, execução paralela por bots e sequência recomendada
- [[secretaria-ai-sistema]] — Visão de produto: triagem→pipeline; integrações WPP/Asana/GAgenda; cronograma 4 meses

## 👥 Stakeholders

- [[amanda-coelho]] — Fundadora/CEO da Assinatura; origina funis e estratégia; decisora final
- [[assinatura-marca-propria]] — Consultoria de marca própria em cosméticos; BH; 2.000+ clientes
- [[gabi]] — Gestora de novos projetos (palestras, expansão); dor: gargalo de tempo; produto: Secretária A.I.
- [[marcelle]] — Gestora do projeto principal; gênio operacional; produto: Automação via WhatsApp

## 🧩 Decisions (ADRs)

- [[adr-001-next-express-separados]] — Frontend e backend como processos distintos no Agente Designer
- [[adr-002-gemini-llm-designer]] — Gemini Flash em vez de GPT-4o para geração de layouts JSON
- [[adr-003-infra-compartilhada]] — FastAPI + Evolution API + Redis + PostgreSQL reaproveitados sem custo extra
- [[adr-004-fabrica-arquitetura-v3]] — ⏳ PENDENTE/ADIADA: substituída pelo modelo híbrido/conversacional atual.
- [[adr-005-canva-api-migração]] — decisão histórica superada pela ADR-006 para edição principal embarcada
- [[adr-006-editor-visual-alternativas-canva]] — **ACEITA (2026-05-11):** CanvasEditor próprio (react-rnd) reativado — embarcado, zero infra extra; Penpot adiado por RAM insuficiente; Fabric.js preterido
- [[adr-007-modularizacao-multimidia]] — **ACEITA (2026-05-24):** Modularização orientada a classes para suportar Instagram, TikTok, Animações e isolar a Typography Engine.

## 📦 Migrations (Consolidações Semanais)

- [[2026-04-22]] — Primeira consolidação: 1 commit designer, 3 gaps de doc identificados
- [[2026-05-03]] — Semana 5 ✅ | Semana 6 🔄 | ADRs criados | Stripe mapeado | gaps ativos listados
- [[2026-05-05]] — **ADR-005 aceita:** Migração CanvasEditor → Canva Connect API | 3 novos docs | 6 docs atualizados

## 📚 Outputs (Queries Arquivadas)

- [[pesquisa-geracao-imagens-pdf-designer]] — Opções e recomendações para conectar a tool "Imagem" (stub) e adicionar export PDF ao CanvasEditor (2026-04-24)
- [[designer-auditoria-jornada]] — Canvas Obsidian: jornada do cliente, auditoria de configurações, gaps por etapa e urgências (2026-04-24)
- [[agentes-mapa-funcoes]] — Canvas Obsidian: Gabi (Fernanda) + Marcelle, funções por status, infraestrutura compartilhada (2026-05-06)
- [[designer-plano-implementacao]] — Sprints, necessidades técnicas, riscos e critérios de aceite para fechar os gaps do Designer (2026-04-24)
- [[auditoria-libs-configs]] — 9 problemas mapeados: L1+L2 resolvidos Sprint 0, L3–L9 em aberto (2026-04-24, atualizado 2026-04-25)
- [[auditoria-ux-logica-designer]] — Sprint 0 concluído; fluxo de config/referencias; gaps UX+segurança; needs para Sprint 1 (2026-04-25)
- [[benchmarking-fabrica-ux]] — Canva/Beautiful.ai/Gamma/Pitch/Slidebean; 5 padrões recorrentes; proposta de layout 3-painéis para a Fábrica (2026-05-04)
- [[calendario-notion-execucao-2026-04-01-2026-05-13]] — Calendário semanal para Notion cobrindo entregas de 01/04 a 13/05 com CSV importável (2026-05-14)
- [[relatorio-entregas-valor-agregado-2026-05-14]] — Relatório executivo separando contratado, adiantamento e entregas adicionais por Gabi, Designer, Marcelle e governança (2026-05-14)
- [[timeline-calendario-obsidian-2026-04-01-2026-05-14]] — Timeline em visão de calendário para Obsidian com semanas, subitens, classificação e links de evidência (2026-05-14)
- [[revisao-contratual-escopo-cronograma-aceite-2026-05-14]] — Minuta técnica/comercial com diagnóstico Gabi vs Marcelle, cronograma paralelo, escopo Marcelle, financeiro e critérios de aceite (2026-05-14)

---

## ðŸ“– Como Navegar

- **VisÃ£o geral rÃ¡pida:** [[overview]]
- **Timeline linear:** [[log]]
- **Timeline visual:** abrir `tracking.canvas` no Obsidian
- **Schema e regras:** [[CLAUDE]]

