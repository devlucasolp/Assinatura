---
title: Escopo do Projeto Assinatura
type: workflow
tags: [assinatura, escopo, contrato, diagnóstico, marcelle, gabi]
sources: [Diagnostico_Assinatura.docx, CONTEXTO.md]
created: 2026-04-22
updated: 2026-04-22
---

# Escopo do Projeto Assinatura

## Resumo

Contrato de prestação de serviços entre Lucas de Oliveira Lopes e Assinatura Consultoria Treinamento e Comercio Ltda, vigente desde 01/04/2026. O projeto entrega dois produtos paralelos: **Secretária A.I. (Gabi)** e **Automação de Projetos (Marcelle)**. O diagnóstico técnico foi concluído para a frente Gabriela; o da Marcelle está em andamento, com sessão presencial pendente.

## Detalhes

### Partes

| Campo | Valor |
|---|---|
| Contratante | Assinatura Consultoria Treinamento e Comercio Ltda |
| CNPJ Contratante | 33.825.369/0001-92 |
| Contratada | Lucas de Oliveira Lopes |
| CNPJ Contratada | 61.418.797/0001-36 |
| Data do Contrato | 01/04/2026 |
| Relatório de Diagnóstico | 15/04/2026 |

### Dois Produtos

| Produto | Responsável | Prazo | Financeiro |
|---|---|---|---|
| Secretária A.I. | Gabriela (Gabi) | 4 meses | R$ 1.200/mês × 10 parcelas |
| Automação de Projetos | Marcelle | 1 mês | R$ 1.000/mês × 10 parcelas |

- Detalhes Gabi → [features/secretaria-ai-gabi.md](../features/secretaria-ai-gabi.md)
- Detalhes Marcelle → [features/automacao-notificacao-marcelle.md](../features/automacao-notificacao-marcelle.md)

### Status do Diagnóstico por Frente

| Frente | Status | Observação |
|---|---|---|
| Gabriela — Expansão/Assessoria | ✅ Concluído | Sessão presencial realizada. Todos os pontos mapeados. |
| Marcelle — Projetos | 🔄 Em andamento | Base levantada via Asana. Diagnóstico presencial pendente. |

### Fluxo Geral de Entrega

```
Diagnóstico (abr/2026)
  → Secretária A.I. — 4 meses (mar–jul/2026)
      ↓ após conclusão
  → Agente Marcelle — inicia usando infraestrutura já pronta
```

## Decisões Tomadas

- **Sequenciamento:** Agente Marcelle inicia após conclusão da Secretária A.I. — foco e reuso de infraestrutura sem custo adicional.
- **Dashboard unificado fora do escopo:** Marcelle mencionou querer "tudo em uma tela" — não está no escopo; formalizar exige UX dedicada e revisão de valor.
- **Dois caminhos para atas (Gabi):** (1) Automático: Gemini → ChatGPT → Asana; (2) Semi-manual: Gabi puxa do Gemini, envia por WhatsApp → Asana.

## Learnings

- O diagnóstico da Marcelle foi indireto (análise do Asana); sessão presencial pendente — escopo final pode expandir.
- A base do agente designer já está construída e funcional, reduzindo risco técnico da fase final da Gabi.
- Infraestrutura compartilhada (Evolution API + EasyPanel) multiplica valor: serve ambas as frentes.

## Relacionados

- [Secretária A.I. (Gabi)](../features/secretaria-ai-gabi.md) — produto 1
- [Automação Marcelle](../features/automacao-notificacao-marcelle.md) — produto 2
- [Infraestrutura Técnica](../integrations/infraestrutura-tecnica.md) — base técnica compartilhada
