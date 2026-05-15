---
title: Index â€” CatÃ¡logo Master da Wiki
type: architecture
tags:
  - "index"
  - "toc"
sources: []
created: 2026-04-22
updated: 2026-05-14
---

# ðŸ—‚ï¸ Index â€” CatÃ¡logo Master

> Toda pÃ¡gina nova da wiki DEVE ser registrada aqui na seÃ§Ã£o correspondente.
> O `/memory-query` usa este arquivo como ponto de partida para localizar conteÃºdo.

## ðŸ›ï¸ Architecture

- [[designer-backend]] â€” Express + Prisma + PostgreSQL + Gemini; rotas, auth middleware, nanoBanana engine e upload R2 validado
- [[designer-frontend]] â€” Next.js App Router, [marca] dynamic routes, FÃ¡brica (chat/SSE), CanvasEditor
- [[agente-multimodelo]] â€” Proposta histÃ³rica LLM + tools; Vercel AI SDK nÃ£o foi implementado; evolução recomenda Gemini pesado + DesignDocument
- [[render-layout-as-data]] â€” JSON layers/DesignDocument â†’ render determinístico; layers seguem como formato compilado/editável
- [[design-document-hibrido]] â€” Proposta de geração por código seguro: Gemini pesado + contexto ampliado â†’ DesignDocument React/CSS â†’ Layer[] compatível com CanvasEditor

## ✨ Features

- [[bot-gabi]] — FastAPI+Python; MVP 1 ✅ (auto-reply) e MVP 2 ✅ (atas→Asana) implementados; deploy EasyPanel
- [[agente-designer]] — App Next.js+Express de geração de designs via Nano Banana (Gemini JSON mode); Sprint 1 🔄
- [[fabrica-v2]] — Novo fluxo wizard 3-steps, preview responsivo e gestão de assets (2026-04-27)
- [[fabrica-redesign]] — ⚠️ CONFLITO com v2; proposta sem wizard, React+Supabase; pendente decisão de arquitetura
- [[fabrica-biblioteca-layouts]] — 6 layouts MVP, layoutKey canônico, metadados, benchmarking de modelos
- [[galeria-gestao]] — Drag-and-drop para pastas, exclusão de artes e atualização reativa (2026-04-27)
- [[design-document-renderer]] — Tipagem estrita e componente de preview seguro para DesignDocument (Code Preview)
- [[secretaria-ai-gabi]] — Agente WhatsApp + atas + gerador de imagens; bot partindo para testes; Drive pendente; execução adiantada (2026-05-13)
- [[secretaria-ai-mes2]] â€” Semanas 5â€“8 | deadline 19/05/2026 | histÃ³rico; status atual avanÃ§ou para testes
- [[automacao-notificacao-marcelle]] â€” 4 meses paralelos, R$ 1.000/mÃªs Ã— 10 | MÃªs 1 âœ… | MÃªs 2 ðŸ”„ teste operacional semana 18/05/2026

## ðŸ”Œ Integrations

- [[infraestrutura-tecnica]] â€” Asana API âœ… + WhatsApp/Evolution API âœ… + EasyPanel + Gemini + ChatGPT
- [[stripe-webhook]] â€” Webhook âœ… | Facebook CAPI âš ï¸ | TikTok CAPI âš ï¸ | UTM âŒ (nÃ£o implementado)
- [[canva-connect-api]] â€” HistÃ³rico/stand-by pÃ³s-ADR-006; nÃ£o Ã© o caminho principal do editor embarcado

## ðŸ” Security

_Nenhuma pÃ¡gina ainda. Criar: JWT httpOnly vs localStorage (ADR pendente)._

## ðŸ”„ Workflows

- [[escopo-projeto-assinatura]] â€” Contrato Lucas Ã— Assinatura Ltda; dois produtos paralelos (Gabi 4m + Marcelle 4m)
- [[qualidade-lint-build]] â€” Lint e build limpos no frontend e backend (2026-04-27)
- [[bot-01-backend-gemini-designdocument]] â€” Brief operacional do bot backend: Gemini pesado, contexto ampliado, endpoint experimental e validação DesignDocument
- [[bot-02-frontend-renderer-designdocument]] â€” Brief operacional do bot frontend: renderer React/CSS seguro para DesignDocument sem mexer no editor
- [[bot-03-compat-editor-auditoria-designdocument]] â€” Brief operacional do bot de compatibilidade: editor/galeria, helpers, auditoria e falsos positivos
- [[designer-timeline-execucao]] — Timeline do Designer atualizada com DesignDocument híbrido, execução paralela por bots e sequência recomendada
- [[secretaria-ai-sistema]] â€” VisÃ£o de produto: triagemâ†’pipeline; integraÃ§Ãµes WPP/Asana/GAgenda; cronograma 4 meses

## ðŸ‘¥ Stakeholders

- [[amanda-coelho]] â€” Fundadora/CEO da Assinatura; origina funis e estratÃ©gia; decisora final
- [[assinatura-marca-propria]] â€” Consultoria de marca prÃ³pria em cosmÃ©ticos; BH; 2.000+ clientes
- [[gabi]] â€” Gestora de novos projetos (palestras, expansÃ£o); dor: gargalo de tempo; produto: SecretÃ¡ria A.I.
- [[marcelle]] â€” Gestora do projeto principal; gÃªnio operacional; produto: AutomaÃ§Ã£o via WhatsApp

## ðŸ§­ Decisions (ADRs)

- [[adr-001-next-express-separados]] â€” Frontend e backend como processos distintos no Agente Designer
- [[adr-002-gemini-llm-designer]] â€” Gemini Flash em vez de GPT-4o para geraÃ§Ã£o de layouts JSON
- [[adr-003-infra-compartilhada]] â€” FastAPI + Evolution API + Redis + PostgreSQL reaproveitados sem custo extra
- [[adr-004-fabrica-arquitetura-v3]] â€” â³ PENDENTE/ADIADA: decisÃ£o fica por Ãºltimo; FÃ¡brica v2/Wizard permanece base operacional
- [[adr-005-canva-api-migraÃ§Ã£o]] â€” decisÃ£o histÃ³rica superada pela ADR-006 para ediÃ§Ã£o principal embarcada
- [[adr-006-editor-visual-alternativas-canva]] â€” **ACEITA (2026-05-11):** CanvasEditor prÃ³prio (react-rnd) reativado â€” embarcado, zero infra extra; Penpot adiado por RAM insuficiente; Fabric.js preterido

## ðŸ“¦ Migrations (ConsolidaÃ§Ãµes Semanais)

- [[2026-04-22]] â€” Primeira consolidaÃ§Ã£o: 1 commit designer, 3 gaps de doc identificados
- [[2026-05-03]] â€” Semana 5 âœ… | Semana 6 ðŸ”„ | ADRs criados | Stripe mapeado | gaps ativos listados
- [[2026-05-05]] â€” **ADR-005 aceita:** MigraÃ§Ã£o CanvasEditor â†’ Canva Connect API | 3 novos docs | 6 docs atualizados

## ðŸ“š Outputs (Queries Arquivadas)

- [[pesquisa-geracao-imagens-pdf-designer]] â€” OpÃ§Ãµes e recomendaÃ§Ãµes para conectar a tool "Imagem" (stub) e adicionar export PDF ao CanvasEditor (2026-04-24)
- [[designer-auditoria-jornada]] â€” Canvas Obsidian: jornada do cliente, auditoria de configuraÃ§Ãµes, gaps por etapa e urgÃªncias (2026-04-24)
- [[agentes-mapa-funcoes]] â€” Canvas Obsidian: Gabi (Fernanda) + Marcelle, funÃ§Ãµes por status, infraestrutura compartilhada (2026-05-06)
- [[designer-plano-implementacao]] â€” Sprints, necessidades tÃ©cnicas, riscos e critÃ©rios de aceite para fechar os gaps do Designer (2026-04-24)
- [[auditoria-libs-configs]] â€” 9 problemas mapeados: L1+L2 resolvidos Sprint 0, L3â€“L9 em aberto (2026-04-24, atualizado 2026-04-25)
- [[auditoria-ux-logica-designer]] â€” Sprint 0 concluÃ­do; fluxo de config/referencias; gaps UX+seguranÃ§a; needs para Sprint 1 (2026-04-25)
- [[benchmarking-fabrica-ux]] â€” Canva/Beautiful.ai/Gamma/Pitch/Slidebean; 5 padrÃµes recorrentes; proposta de layout 3-painÃ©is para a FÃ¡brica (2026-05-04)
- [[calendario-notion-execucao-2026-04-01-2026-05-13]] â€” CalendÃ¡rio semanal para Notion cobrindo entregas de 01/04 a 13/05 com CSV importÃ¡vel (2026-05-14)
- [[relatorio-entregas-valor-agregado-2026-05-14]] — Relatório executivo separando contratado, adiantamento e entregas adicionais por Gabi, Designer, Marcelle e governança (2026-05-14)
- [[timeline-calendario-obsidian-2026-04-01-2026-05-14]] — Timeline em visão de calendário para Obsidian com semanas, subitens, classificação e links de evidência (2026-05-14)
- [[revisao-contratual-escopo-cronograma-aceite-2026-05-14]] — Minuta técnica/comercial com diagnóstico Gabi vs Marcelle, cronograma paralelo, escopo Marcelle, financeiro e critérios de aceite (2026-05-14)

---

## ðŸ“– Como Navegar

- **VisÃ£o geral rÃ¡pida:** [[overview]]
- **Timeline linear:** [[log]]
- **Timeline visual:** abrir `tracking.canvas` no Obsidian
- **Schema e regras:** [[CLAUDE]]

