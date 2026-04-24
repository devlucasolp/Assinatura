---
title: Automação de Notificação (Marcelle)
type: feature
tags: [marcelle, asana, whatsapp, reports, projetos, automação, erm, dashboard]
sources: [Diagnostico_Assinatura.docx, CONTEXTO.md]
created: 2026-04-22
updated: 2026-04-22
---

# Automação de Notificação (Marcelle)

## Resumo

Sistema de visibilidade, estimativas e automação do fluxo de projetos para Marcelle (frente de projetos). Prazo de 1 mês (4 semanas) com 1 MVP por semana. Início: 24/03/2026 — Entrega final: 21/04/2026. Financiamento via Mercado Pago: R$ 1.000/mês × 10 parcelas. O diagnóstico presencial com Marcelle ainda está pendente.

## Detalhes

### Cronograma

| Semana | Período | Fase | Desenvolvimento | MVP |
|---|---|---|---|---|
| Semana 1 | 24–31/03 | Infraestrutura e Dados | Estruturação do ERM interno + conexão com dados do Asana | MVP 1 — Base de dados e integração inicial funcionando |
| Semana 2 | 01–07/04 | Lógica de Negócio | Cálculo de estimativa de tempo operacional | MVP 2 — Regras de cálculo e precisão do tempo validadas |
| Semana 3 | 08–14/04 | Visualização | Dashboards e reports internos | MVP 3 — Geração de relatórios com dados reais |
| Semana 4 | 15–21/04 | Polimento e Lançamento | Correção de bugs, refinamento e validação final integrada | MVP 4 — Fluxo completo validado e entrega oficial |

### Features Mapeadas

- **Controle de estágio do cliente** — visibilidade de onde cada projeto está no ciclo de vida
- **Agente reativo no WhatsApp** — Marcelle pergunta "como está o projeto X?" → resposta automática com status atualizado
- **Visualização interna e para o cliente** — funil de projetos, erros e atrasos (lado empresa + lado cliente)
- **Reports automáticos** — alertas sobre atrasos ou erros no andamento dos projetos
- **Fusão com infraestrutura da Gabi** — Agente Marcelle inicia após Secretária A.I., sem acréscimo de custo

### Fora do Escopo

- **Dashboard unificado** ("sonho" de Marcelle — ver tudo em uma tela): formalizar exige UX dedicada e revisão de valor contratual.

### Financeiro

| Campo | Valor |
|---|---|
| Gateway | Mercado Pago |
| Parcelas | R$ 1.000/mês × 10 |
| Status | ⚠️ Pendente: confirmar juros e número exato com gerente do Mercado Pago |

## Decisões Tomadas

- Diagnóstico presencial com Marcelle pendente — escopo acordado é base mínima; pode expandir após sessão.
- Agente Marcelle inicia após Secretária A.I. para garantir foco na entrega de cada solução.
- **Base técnica:** reaproveitamento direto do `Bot_Gabi/` (FastAPI + Evolution API + Redis + PostgreSQL + EasyPanel) — apenas handlers e lógica de negócio próprios da Marcelle serão novos. Zero custo adicional de infraestrutura.

## Learnings

- ERM e integração Asana são o alicerce — atrasos na Semana 1 propagam para todas as semanas seguintes.
- Diagnóstico indireto (via Asana) é fonte de incerteza de escopo — realizar sessão presencial o quanto antes para reduzir risco.

## Relacionados

- [Escopo do Projeto Assinatura](../workflows/escopo-projeto-assinatura.md) — contrato e visão geral
- [Bot Gabi](bot-gabi.md) — base de código que será reaproveitada (FastAPI + Evolution API + Redis + PostgreSQL)
- [Secretária A.I. (Gabi)](secretaria-ai-gabi.md) — produto Gabi entregue antes
- [Infraestrutura Técnica](../integrations/infraestrutura-tecnica.md) — Asana API, WhatsApp, Evolution API
