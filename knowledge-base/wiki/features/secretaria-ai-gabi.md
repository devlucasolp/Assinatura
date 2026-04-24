---
title: Secretária A.I. (Gabi)
type: feature
tags: [gabi, whatsapp, asana, gemini, chatgpt, agente, apresentações, artes, designer]
sources: [Diagnostico_Assinatura.docx, CONTEXTO.md]
created: 2026-04-22
updated: 2026-04-22
---

# Secretária A.I. (Gabi)

## Resumo

Agente multi-funcional de comunicação, gestão de tarefas e geração de ativos para Gabriela (frente de expansão de novos negócios e assessoria). Prazo de 4 meses com 1 MVP por mês. Início: 24/03/2026 — Entrega final: 14/07/2026. Financiamento via Mercado Pago: R$ 1.200/mês × 10 parcelas.

## Detalhes

### Cronograma

| Mês | Período | Fase | Desenvolvimento | MVP |
|---|---|---|---|---|
| Mês 1 | 24/03–21/04 | Mensagens Automáticas | Agente WhatsApp para ausências em reuniões/eventos | MVP 1 — Agente respondendo automaticamente durante ausências |
| Mês 2 | 22/04–19/05 | Atas de Reunião | Pipeline Gemini → ChatGPT → Asana (automático e semi-manual) | MVP 2 — Ata gerada e publicada automaticamente no Asana |
| Mês 3 | 20/05–16/06 | Gerador de Imagens (Testes) | Agente gerador de imagens/apresentações + ciclos de validação | MVP 3 — Gerador funcional em ambiente de testes |
| Mês 4 | 17/06–14/07 | Validação e Lançamento | Revisão de todos os módulos + validação final do gerador | MVP 4 — Lançamento oficial da Secretária A.I. |

### Features Mapeadas

- **Mensagens automáticas no WhatsApp** — resposta automática quando Gabi está em reunião ou evento
- **Atas de reunião** — dois caminhos:
  - Automático: Gemini gera → ChatGPT lapida os pontos → publica no Asana
  - Semi-manual: Gabi puxa do Gemini, envia por WhatsApp → automação → Asana
- **Agente Designer** — interface UX externa ao WhatsApp para geração de apresentações e artes de forma autônoma
- **Gerador de imagens e apresentações** — última fase; maior esforço de teste e validação

### Financeiro

| Campo | Valor |
|---|---|
| Gateway | Mercado Pago |
| Parcelas | R$ 1.200/mês × 10 |
| Status | ⚠️ Pendente: confirmar juros e número exato com gerente do Mercado Pago |

## Decisões Tomadas

- Gerador de imagens posicionado no Mês 3/4 — maior risco técnico, mais tempo para testes e validação.
- Interface UX externa ao WhatsApp para operações visuais complexas — WhatsApp não é adequado para esse fluxo.
- Base do agente designer já construída → menor incerteza técnica nas fases finais.

## Learnings

- A base do agente designer já está funcional; o risco principal agora é integração completa e qualidade de output.
- O pipeline de dois LLMs (Gemini gera, ChatGPT lapida) foi escolhido por qualidade — monitorar latência e custo.

## Relacionados

- [Escopo do Projeto Assinatura](../workflows/escopo-projeto-assinatura.md) — contrato e visão geral
- [Automação Marcelle](automacao-notificacao-marcelle.md) — reutiliza esta infraestrutura após Mês 4
- [Infraestrutura Técnica](../integrations/infraestrutura-tecnica.md) — Asana API, WhatsApp, Evolution API, Gemini, ChatGPT
