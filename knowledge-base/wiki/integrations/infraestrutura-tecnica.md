---
title: Infraestrutura Técnica Atual
type: integration
tags: [asana, whatsapp, evolution-api, easypanel, gemini, chatgpt, agente-designer, infraestrutura]
sources: [Diagnostico_Assinatura.docx]
created: 2026-04-22
updated: 2026-04-22
---

# Infraestrutura Técnica Atual

## Resumo

Estado da infraestrutura técnica levantada durante o diagnóstico (abril 2026). Asana API e WhatsApp via Evolution API já estão operacionais. O Agente Designer tem base funcional, aguardando integração completa. O Agente Marcelle ainda não foi iniciado — aguarda conclusão da Secretária A.I.

## Detalhes

### Status por Componente (referência: 15/04/2026)

| Componente | Status | Observação |
|---|---|---|
| Asana API | ✅ Concluído | Integração ativa — criação de tasks via API funcionando |
| WhatsApp + Evolution API | ✅ Concluído | Integrado e operacional via EasyPanel |
| Agente Designer | 🔄 Em andamento | Base criada e funcional, aguarda integração completa |
| Agente Marcelle | ⏳ Pendente | Iniciará após conclusão da Secretária A.I. |

### Componentes e Papéis

| Componente | Papel |
|---|---|
| **Asana API** | Criação e atualização de tasks; base de todos os flows de automação |
| **WhatsApp + Evolution API** | Canal principal de comunicação dos agentes |
| **EasyPanel** | Plataforma de hospedagem dos serviços de backend |
| **Gemini** | LLM para geração de atas de reunião (input do pipeline) |
| **ChatGPT** | Lapidação dos pontos gerados pelo Gemini antes de publicar no Asana |
| **Agente Designer** | Geração autônoma de apresentações e artes (UX externa ao WhatsApp) |

### Pipeline de Atas (dois caminhos)

```
Caminho Automático:
  Reunião → Gemini (transcrição/geração) → ChatGPT (lapidação) → Asana (task)

Caminho Semi-manual:
  Reunião → Gabi puxa do Gemini → envia por WhatsApp → automação → Asana
```

## Decisões Tomadas

- Evolution API via EasyPanel escolhida para WhatsApp — já operacional e estável.
- Pipeline de atas usa dois LLMs: Gemini gera, ChatGPT lapida — trade-off de latência por qualidade de output.
- Infraestrutura compartilhada entre Gabi e Marcelle — sem custo adicional para o segundo agente.

## Learnings

- A infraestrutura compartilhada (Evolution API + EasyPanel) multiplica valor: serve ambas as frentes sem custo adicional.
- O pipeline Gemini → ChatGPT adiciona uma chamada de API extra — monitorar custo operacional ao escalar.

## Relacionados

- [Secretária A.I. (Gabi)](../features/secretaria-ai-gabi.md) — consumidora principal desta infraestrutura
- [Automação Marcelle](../features/automacao-notificacao-marcelle.md) — reutilizará após conclusão da Gabi
- [Escopo do Projeto Assinatura](../workflows/escopo-projeto-assinatura.md) — contexto geral do projeto
