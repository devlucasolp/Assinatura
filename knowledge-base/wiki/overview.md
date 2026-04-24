---
title: Overview — Síntese Dinâmica
type: architecture
tags: [overview, synthesis]
sources: []
created: 2026-04-22
updated: 2026-04-22
---

# 🗺️ Overview — Síntese Dinâmica do Projeto

> Este arquivo é **sobrescrito** por `/memory-consolidate` com base na semana corrente.
> Não editar à mão em seções geradas (marcadas com `<!-- auto -->`).

## Estado Atual

Primeira consolidação realizada em 2026-04-22. Wiki populada com diagnóstico do projeto (Diagnostico_Assinatura.docx + CONTEXTO.md). O repositório git (`designer/`) contém o Agente Designer em initial commit de 19/04/2026. A Automação Marcelle não tem commits — verificar status.

## Pilares Arquiteturais

<!-- auto:pillars -->
- [Arquitetura Backend](architecture/designer-backend.md) — Express + Prisma + PostgreSQL + Gemini (dual-key: chat vs design)
- [Arquitetura Frontend](architecture/designer-frontend.md) — Next.js App Router, [marca] scoping, SSE streaming, CanvasEditor
<!-- /auto:pillars -->

## Features em Produção

<!-- auto:features -->
- [Agente Designer](features/agente-designer.md) — App designer IA | git: `e809a0f` (19/04) | gaps: save configs, auth nas rotas
- [Secretária A.I. (Gabi)](features/secretaria-ai-gabi.md) — Agente WhatsApp + atas + gerador de imagens | 4 meses | até 14/07/2026 | Mês 1 ✅ (21/04)
- [Automação de Notificação (Marcelle)](features/automacao-notificacao-marcelle.md) — Visibilidade Asana via WhatsApp | 1 mês | prazo 21/04/2026 ⚠️ verificar status
<!-- /auto:features -->

## Integrações Ativas

<!-- auto:integrations -->
- [Infraestrutura Técnica Atual](integrations/infraestrutura-tecnica.md) — Asana API ✅ · WhatsApp + Evolution API ✅ · EasyPanel ✅ · Agente Designer 🔄 · Agente Marcelle ⏳
<!-- /auto:integrations -->

## Decisões Recentes

<!-- auto:decisions -->
_Nenhuma ADR ainda. Criar ADRs para: (1) Next.js + Express separados, (2) Gemini como LLM do Designer, (3) infraestrutura compartilhada Gabi → Marcelle._
<!-- /auto:decisions -->

## Dívida Técnica Conhecida

<!-- auto:debt -->
_(populado por `/memory-lint`)_
<!-- /auto:debt -->

---

## Como Manter

- Seções automáticas: não tocar — `/memory-consolidate` cuida.
- Seções livres (ex: "Estado Atual"): pode editar à mão; consolidate preserva.
