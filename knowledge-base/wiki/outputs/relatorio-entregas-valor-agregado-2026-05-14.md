---
title: "Relatório de Entregas e Valor Agregado — Projeto Assinatura"
type: output
tags:
  - "relatorio"
  - "valor-agregado"
  - "contrato"
  - "gabi"
  - "designer"
  - "marcelle"
sources:
  - "wiki/workflows/escopo-projeto-assinatura.md"
  - "wiki/features/secretaria-ai-gabi.md"
  - "wiki/features/bot-gabi.md"
  - "wiki/features/automacao-notificacao-marcelle.md"
  - "wiki/features/agente-designer.md"
  - "wiki/outputs/calendario-notion-execucao-2026-04-01-2026-05-13.md"
  - "wiki/overview.md"
  - "wiki/outputs/revisao-contratual-escopo-cronograma-aceite-2026-05-14.md"
created: 2026-05-14
updated: 2026-05-14
---

# Relatório de Entregas e Valor Agregado — Projeto Assinatura

## Resumo executivo

> Nota de alinhamento: este relatório deve ser lido junto com [[revisao-contratual-escopo-cronograma-aceite-2026-05-14]], que explicita diagnóstico Gabi vs Marcelle, cronograma paralelo, escopo objetivo da Marcelle, estrutura financeira registrada e critérios de aceite dos MVPs.

Entre 01/04/2026 e 14/05/2026, o projeto avançou além do ritmo contratual previsto: a frente **Secretária A.I. da Gabi** já tem MVP 1 e MVP 2 implementados, o **Designer IA** saiu da fundação para um produto navegável com Fábrica, Galeria, Editor visual e revisão IA, e a frente **Marcelle** teve Mês 1 consolidado e preparação para teste operacional.

A leitura correta das entregas precisa separar três grupos:

1. **Entregas contratadas:** itens previstos no escopo original.
2. **Entregas contratadas adiantadas:** itens previstos, mas realizados antes do período esperado.
3. **Entregas adicionais:** recursos, robustez técnica, governança, editor visual, fluxos e melhorias que excedem o mínimo contratual.

O ponto principal: **as entregas adicionais não são a existência dos MVPs da Gabi em si**, porque eles estavam contratados. O valor agregado está na profundidade técnica, nas features adicionais do bot, na robustez do Designer, nos fluxos de revisão, na rastreabilidade e na antecipação de fases.

## Base contratual usada

### Produto 1 — Secretária A.I. + Designer Gabi

Fonte: [[secretaria-ai-gabi]], [[escopo-projeto-assinatura]].

| Mês | Período | Fase contratada | MVP contratado | Status em 14/05 |
|---|---|---|---|---|
| Mês 1 | 24/03–21/04 | Mensagens Automáticas | Agente WhatsApp respondendo automaticamente durante ausências | Entregue |
| Mês 2 | 22/04–19/05 | Atas de Reunião | Ata gerada e publicada automaticamente no Asana | Entregue antecipadamente |
| Mês 3 | 20/05–16/06 | Gerador de Imagens/Testes | Gerador funcional em ambiente de testes | Adiantado |
| Mês 4 | 17/06–14/07 | Validação e Lançamento | Lançamento oficial da Secretária A.I. | Parcialmente adiantado |

### Produto 2 — Automação de Notificação Marcelle

Fonte: [[automacao-notificacao-marcelle]], [[escopo-projeto-assinatura]].

| Mês | Período | Fase contratada | MVP contratado | Status em 14/05 |
|---|---|---|---|---|
| Mês 1 | 24/03–21/04 | Infraestrutura + Consultoria | Base de dados e automação Asana funcionando | Entregue |
| Mês 2 | 22/04–19/05 | Preparação de teste | Teste operacional com Marcelle | Previsto para semana de 18/05 |
| Mês 3 | 20/05–16/06 | Ajustes pós-teste | Fluxo validado/refinado | Aguardando teste |
| Mês 4 | 17/06–14/07 | Lançamento e estabilização | Operação estável | Não iniciado |

## Classificação geral

### Contratado, não adicional

Estes itens devem aparecer como entregas do contrato, não como bônus:

- Auto-reply WhatsApp em reuniões/eventos — MVP 1 da Gabi.
- Atas de reunião publicadas no Asana — MVP 2 da Gabi.
- Agente Designer / gerador de imagens e apresentações — MVP 3/4 da Gabi.
- Infraestrutura mínima WhatsApp + Asana + IA necessária para executar os MVPs.
- Base de dados e automação Asana da Marcelle — Mês 1 Marcelle.

### Contratado, mas entregue adiantado

Estes itens não são bônus funcionais, mas são **adiantamento de escopo**:

- MVP 2 da Gabi entregue junto do MVP 1.
- Base do Designer iniciada antes da janela formal do Mês 3.
- Designer já partindo para testes antes do início formal do Mês 3 em 20/05/2026.
- Marcelle com Mês 1 entregue e Mês 2 encaminhado para teste operacional.

### Entregas adicionais

Entregas adicionais são itens não exigidos explicitamente no contrato ou entregues com profundidade acima do mínimo esperado.

## Features bônus — Gabi Bot

Fonte principal: [[bot-gabi]].

### 1. CRUD de tarefas Asana via WhatsApp

**Classificação:** entrega adicional.

O contrato previa atas no Asana. O bot foi além e passou a operar tarefas diretamente pelo WhatsApp.

Subitens:

- Criar tarefa no Asana por linguagem natural.
- Atualizar tarefa existente.
- Concluir tarefa.
- Deletar tarefa.
- Buscar tarefa.
- Retornar link da última tarefa criada.
- Extrair nome, prazo, projeto e alteração com IA.
- Usar keyword match e fallback LLM para classificar intenção.

Impacto:

- Transforma a Secretária A.I. em assistente operacional, não apenas em gerador de atas.

### 2. Processamento de áudio no WhatsApp

**Classificação:** entrega adicional.

Subitens:

- Detectar áudio recebido.
- Transcrever/interpretar com Gemini.
- Enfileirar a transcrição no fluxo de mensagens.
- Combinar áudio + texto no mesmo contexto.
- Reduzir dependência de digitação manual.

Impacto:

- Aproxima o bot da forma real de uso da Gabi no WhatsApp.

### 3. Processamento de imagem no WhatsApp

**Classificação:** entrega adicional.

Subitens:

- Detectar imagem recebida.
- Descrever/interpretar imagem com Gemini.
- Converter leitura visual em texto operacional.
- Enfileirar resultado no debounce.
- Preparar base para fluxos futuros com referências visuais.

Impacto:

- Expande o bot para além de texto e áudio, criando entrada multimodal.

### 4. Debounce inteligente de mensagens

**Classificação:** melhoria técnica de experiência.

Subitens:

- Agrupar mensagens enviadas em sequência.
- Aguardar janela de silêncio antes de processar.
- Evitar múltiplas respostas quebradas.
- Reduzir chamadas LLM.
- Melhorar compreensão de mensagens fragmentadas.

Impacto:

- Reduz custo e melhora naturalidade conversacional.

### 5. Estado pendente para fluxos multi-turno

**Classificação:** melhoria técnica.

Subitens:

- Guardar ações pendentes em Redis.
- Continuar fluxos após respostas curtas.
- Interpretar confirmações como “sim”, “pode”, “confirma”.
- Evitar que respostas curtas caiam no chat geral.

Impacto:

- Permite comportamento mais próximo de secretária real, com confirmação e continuidade.

### 6. Controle anti-loop e filtro de mensagens próprias

**Classificação:** melhoria de confiabilidade.

Subitens:

- Ignorar mensagens `fromMe`.
- Evitar que o bot responda às próprias mensagens.
- Tratar exceções para triggers específicos.
- Reduzir risco de loop em produção.

Impacto:

- Aumenta segurança operacional do webhook.

### 7. Controle de repetição no auto-reply

**Classificação:** melhoria sobre item contratado.

Auto-reply era contratado; o controle de repetição por contato é refinamento adicional.

Subitens:

- Registrar contatos já respondidos.
- Aplicar TTL por número.
- Evitar múltiplas respostas durante a mesma janela de ausência.
- Separar mensagem de reunião e evento.

Impacto:

- Evita experiência ruim para contatos que enviam várias mensagens.

### 8. Estratégia dual LLM

**Classificação:** melhoria arquitetural.

Subitens:

- Gemini para extração estruturada, atas e mídia.
- GPT-4o para chat geral e classificação de intenção.
- Keyword match antes de LLM.
- Fallback para chat geral.
- Otimização por custo, latência e qualidade.

Impacto:

- Arquitetura mais robusta que bot monomodelo simples.

### 9. Histórico conversacional em PostgreSQL

**Classificação:** melhoria técnica.

Subitens:

- Salvar histórico de conversas.
- Consultar últimos turnos.
- Alimentar chat geral com contexto recente.
- Criar base futura para auditoria e relatórios.

Impacto:

- Dá memória operacional e rastreabilidade ao assistente.

### 10. Degradação graceful de Redis/PostgreSQL

**Classificação:** melhoria de resiliência.

Subitens:

- Bot sobe mesmo se dependências estiverem temporariamente indisponíveis.
- Falha de Redis/PostgreSQL não derruba todo o serviço.
- Mantém operação parcial em caso de instabilidade.

Impacto:

- Melhora confiabilidade real de produção.

## Features bônus — Designer Gabi

Fonte principal: [[agente-designer]], [[designer-backend]], [[designer-frontend]], [[overview]].

### 1. Editor visual próprio com CanvasEditor

**Classificação:** profundidade adicional provável.

O contrato previa gerador de imagens/apresentações. Um editor visual próprio com camadas é uma profundidade acima do mínimo.

Subitens:

- Canvas com layers.
- Drag/resize.
- Sidebar de camadas.
- Painéis de propriedades.
- Texto, imagem e shape editáveis.
- Correções de crashes/null layers.
- Editor embarcado no app, sem depender exclusivamente de ferramenta externa.

Impacto:

- Transforma o gerador em produto editável e operacional.

### 2. Galeria com pastas e drag-and-drop

**Classificação:** profundidade adicional provável.

Subitens:

- Galeria de posts.
- Pastas.
- Drag-and-drop.
- Exclusão.
- Preview modal.
- Organização por marca.
- Abertura no editor.

Impacto:

- Cria gestão operacional de ativos, não só geração de imagens.

### 3. Multi-select e edição em lote no editor

**Classificação:** entrega adicional.

Subitens:

- Seleção múltipla.
- Marquee selection.
- Multi-drag.
- Alinhamento em lote.
- Distribuição horizontal/vertical.
- Atalhos em massa.
- Edição em lote de textos.

Impacto:

- Aproxima o editor de uma ferramenta visual profissional.

### 4. Revisão IA com aprovação humana

**Classificação:** entrega adicional.

Subitens:

- Análise automática do design.
- Plano de correções.
- Seleção humana das correções.
- Aplicação apenas dos ajustes aprovados.
- Retorno de páginas corrigidas.
- Job recuperável de revisão.

Impacto:

- Cria processo de qualidade assistido por IA, em vez de apenas “gerar novamente”.

### 5. Jobs recuperáveis para geração/revisão

**Classificação:** melhoria técnica.

Subitens:

- `create-job`.
- `fix-design-job`.
- Status recuperável.
- Stream por `jobId`.
- Replay de eventos.
- Tratamento de erro.
- TTL em memória.

Impacto:

- Melhora estabilidade em processos longos de IA.

### 6. Regra global de contraste

**Classificação:** melhoria de qualidade visual.

Subitens:

- Texto branco em fundo escuro.
- Texto preto em fundo claro.
- Box translúcido sobre imagem/foto/gradiente.
- Controles editáveis no painel.
- Pós-processamento defensivo no backend.

Impacto:

- Aumenta legibilidade e qualidade visual dos materiais.

### 7. Imagens contextuais por slide

**Classificação:** profundidade adicional provável.

Subitens:

- Primeiro entende o roteiro.
- Depois calcula zonas de texto.
- Só então gera imagem contextual.
- Logo tratado como identidade visual.
- Imagem vira asset do slide.
- Evita geração solta/desconectada.

Impacto:

- Geração visual passa a respeitar narrativa, marca e composição.

## Valor agregado em gestão, arquitetura e qualidade

Estes itens não são “features da Gabi” diretamente, mas fortalecem o projeto.

### 1. KB viva e rastreável

**Classificação:** governança adicional.

Subitens:

- `index.md`.
- `log.md` append-only.
- `overview.md`.
- Outputs para Notion/Obsidian.
- Registro de features, arquitetura, integrações e decisões.

Impacto:

- Facilita prestação de contas e continuidade do projeto.

### 2. ADRs formais

**Classificação:** arquitetura adicional.

Subitens:

- ADR-001 — Next + Express separados.
- ADR-002 — Gemini como LLM principal do Designer.
- ADR-003 — Infraestrutura compartilhada Gabi/Marcelle.
- ADR-005 — Canva API como caminho histórico.
- ADR-006 — CanvasEditor próprio como decisão final.

Impacto:

- Registra racional técnico e evita decisões tácitas.

### 3. Auditorias técnicas e de UX

**Classificação:** qualidade adicional.

Subitens:

- Auditoria de jornada.
- Auditoria UX/lógica.
- Auditoria geral Designer.
- Auditoria de libs/configs.
- Correção de riscos P0/P1.

Impacto:

- Reduz risco antes de teste real com usuárias.

### 4. Benchmarking UX

**Classificação:** produto adicional.

Subitens:

- Canva.
- Gamma.
- Beautiful.ai.
- Pitch/Slidebean.
- Padrões de UI/UX extraídos.
- Propostas de evolução da Fábrica.

Impacto:

- Produto passa a ser comparado com ferramentas de mercado.

### 5. Infraestrutura compartilhada Gabi ↔ Marcelle

**Classificação:** ganho estratégico.

Subitens:

- FastAPI.
- Evolution API.
- Redis.
- PostgreSQL.
- EasyPanel.
- Asana API.
- Handlers reaproveitáveis.

Impacto:

- Reduz custo e tempo da frente Marcelle.

## Entregas por semana

| Semana | Período | Entregas principais | Classificação |
|---|---|---|---|
| Semana 1 | 01/04–06/04 | Preparação operacional e execução anterior à KB canônica | Base contratual |
| Semana 2 | 07/04–13/04 | Bot Gabi MVP 1/2, mídia, handlers Asana, Redis, PostgreSQL | Contratado + features bônus bot |
| Semana 3 | 14/04–20/04 | Base inicial do Designer | Contratado adiantado |
| Semana 4 | 21/04–27/04 | KB, Sprint 0, Fábrica v2, Galeria, qualidade | Contratado + valor agregado em gestão/produto |
| Semana 5 | 28/04–04/05 | ADRs, benchmarking, biblioteca de layouts, consolidação | Valor agregado em governança/produto |
| Semana 6 | 05/05–11/05 | ADR-006, CanvasEditor próprio, backend robusto, folders/upload | Valor agregado no Designer |
| Semana 7 | 12/05–14/05 | Multi-select, revisão IA, jobs, contraste, rotas, upload/R2 | Valor agregado no Designer + qualidade |

## Pendências reais após 14/05

- Validação real com Gabi.
- Integração Google Drive no ecossistema Gabi.
- Teste operacional Marcelle na semana de 18/05/2026.
- Persistência de jobs em banco, se o requisito evoluir para retomada pós-restart.
- Fechamento de decisões pendentes da Fábrica após teste com usuária.

## Conclusão

A execução está adiantada e com valor agregado material. O principal cuidado na comunicação é não chamar de “bônus” aquilo que estava contratado. O posicionamento correto é:

- **MVP 1 e MVP 2:** contratados e entregues cedo.
- **Designer:** contratado, mas implementado com profundidade acima do mínimo.
- **Bot Gabi:** features adicionais nos recursos operacionais, mídia, estado, confiabilidade e arquitetura.
- **Projeto:** valor agregado em governança, documentação, ADRs, auditorias e infraestrutura compartilhada.

## Relacionados

- [[escopo-projeto-assinatura]]
- [[secretaria-ai-gabi]]
- [[bot-gabi]]
- [[automacao-notificacao-marcelle]]
- [[agente-designer]]
- [[designer-backend]]
- [[designer-frontend]]
- [[calendario-notion-execucao-2026-04-01-2026-05-13]]
- [[revisao-contratual-escopo-cronograma-aceite-2026-05-14]]
