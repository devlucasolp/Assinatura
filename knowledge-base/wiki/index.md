---
title: Index — Catálogo Master da Wiki
type: architecture
tags: [index, toc]
sources: []
created: 2026-04-22
updated: 2026-04-27
---

# 🗂️ Index — Catálogo Master

> Toda página nova da wiki DEVE ser registrada aqui na seção correspondente.
> O `/memory-query` usa este arquivo como ponto de partida para localizar conteúdo.

## 🏛️ Architecture

- [Arquitetura Backend — Designer](architecture/designer-backend.md) — Express + Prisma + PostgreSQL + Gemini; rotas, auth middleware, nanoBanana engine
- [Arquitetura Frontend — Designer](architecture/designer-frontend.md) — Next.js App Router, [marca] dynamic routes, Fábrica (chat/SSE), CanvasEditor

## ✨ Features

- [Bot Gabi — Secretária A.I.](features/bot-gabi.md) — FastAPI+Python; MVP 1✅ (auto-reply) e MVP 2✅ (atas→Asana) já implementados; deploy EasyPanel
- [Agente Designer](features/agente-designer.md) — App Next.js+Express de geração de designs via Nano Banana (Gemini JSON mode); base funcional no git
- [Fábrica v2 — Redesign Procedural](features/fabrica-v2.md) — Novo fluxo wizard 3-steps, preview responsivo e gestão de assets (2026-04-27)
- [Galeria — Gestão de Ativos](features/galeria-gestao.md) — Drag-and-drop para pastas, exclusão de artes e atualização reativa (2026-04-27)
- [Secretária A.I. (Gabi)](features/secretaria-ai-gabi.md) — Agente WhatsApp + atas de reunião + gerador de imagens; 4 meses, R$ 1.200/mês × 10
- [Automação de Notificação (Marcelle)](features/automacao-notificacao-marcelle.md) — Visibilidade de projetos via WhatsApp + reports Asana; 1 mês, R$ 1.000/mês × 10

## 🔌 Integrations

- [Infraestrutura Técnica Atual](integrations/infraestrutura-tecnica.md) — Asana API ✅ + WhatsApp/Evolution API ✅ + EasyPanel + Gemini + ChatGPT

## 🔐 Security

_Nenhuma página ainda._

## 🔄 Workflows

- [Escopo do Projeto Assinatura](workflows/escopo-projeto-assinatura.md) — Contrato Lucas × Assinatura Ltda; dois produtos paralelos (Gabi 4m + Marcelle 1m)
- [Qualidade — Lint e Build (Designer)](workflows/qualidade-lint-build.md) — Lint e build limpos no frontend e backend (2026-04-27)

## 👥 Stakeholders

- [Amanda Coelho](stakeholders/amanda-coelho.md) — Fundadora/CEO da Assinatura; origina funis e estratégia; decisora final
- [Assinatura Marca Própria](stakeholders/assinatura-marca-propria.md) — Consultoria de marca própria em cosméticos; BH; 2.000+ clientes
- [Gabi](stakeholders/gabi.md) — Gestora de novos projetos (palestras, expansão); dor: gargalo de tempo; produto: Secretária A.I.
- [Marcelle](stakeholders/marcelle.md) — Gestora do projeto principal; gênio operacional; produto: Automação via WhatsApp

## 🧭 Decisions (ADRs)

_Nenhuma página ainda._

## 📦 Migrations (Consolidações Semanais)

- [2026-04-22](migrations/2026-04-22.md) — Primeira consolidação: 1 commit designer, 3 gaps de doc identificados

## 📚 Outputs (Queries Arquivadas)

- [Pesquisa — Geração de Imagens e PDF no Designer](outputs/pesquisa-geracao-imagens-pdf-designer.md) — Opções e recomendações para conectar a tool "Imagem" (stub) e adicionar export PDF ao CanvasEditor (2026-04-24)
- [Auditoria Designer — Jornada da Gabi](outputs/designer-auditoria-jornada.canvas) — Canvas Obsidian: jornada do cliente, auditoria de configurações, gaps por etapa e urgências (2026-04-24)
- [Plano de Implementação — MVP 3 e 4](outputs/designer-plano-implementacao.md) — Sprints, necessidades técnicas, riscos e critérios de aceite para fechar os gaps do Designer (2026-04-24)
- [Auditoria — Libs e Configs](outputs/auditoria-libs-configs.md) — 9 problemas mapeados: L1+L2 resolvidos Sprint 0, L3–L9 em aberto (2026-04-24, atualizado 2026-04-25)
- [Auditoria — UX, Lógica e Necessidades do Designer](outputs/auditoria-ux-logica-designer.md) — Sprint 0 concluído; fluxo de config/referencias; gaps UX+segurança; needs para Sprint 1 (2026-04-25)

---

## 📖 Como Navegar

- **Visão geral rápida:** [`overview.md`](overview.md)
- **Timeline linear:** [`log.md`](log.md)
- **Timeline visual:** abrir `tracking.canvas` no Obsidian
- **Schema e regras:** [`../CLAUDE.md`](../CLAUDE.md)
