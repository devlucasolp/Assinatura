---
title: Index — Catálogo Master da Wiki
type: architecture
tags: [index, toc]
sources: []
created: 2026-04-22
updated: 2026-04-22
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
- [Secretária A.I. (Gabi)](features/secretaria-ai-gabi.md) — Agente WhatsApp + atas de reunião + gerador de imagens; 4 meses, R$ 1.200/mês × 10
- [Automação de Notificação (Marcelle)](features/automacao-notificacao-marcelle.md) — Visibilidade de projetos via WhatsApp + reports Asana; 1 mês, R$ 1.000/mês × 10

## 🔌 Integrations

- [Infraestrutura Técnica Atual](integrations/infraestrutura-tecnica.md) — Asana API ✅ + WhatsApp/Evolution API ✅ + EasyPanel + Gemini + ChatGPT

## 🔐 Security

_Nenhuma página ainda._

## 🔄 Workflows

- [Escopo do Projeto Assinatura](workflows/escopo-projeto-assinatura.md) — Contrato Lucas × Assinatura Ltda; dois produtos paralelos (Gabi 4m + Marcelle 1m)

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

_Nenhuma query arquivada ainda._

---

## 📖 Como Navegar

- **Visão geral rápida:** [`overview.md`](overview.md)
- **Timeline linear:** [`log.md`](log.md)
- **Timeline visual:** abrir `tracking.canvas` no Obsidian
- **Schema e regras:** [`../CLAUDE.md`](../CLAUDE.md)
