---
title: "Revisão Contratual — Escopo, Cronograma, Financeiro e Aceite"
type: output
tags:
  - "contrato"
  - "escopo"
  - "cronograma"
  - "financeiro"
  - "aceite"
  - "gabi"
  - "marcelle"
sources:
  - "wiki/workflows/escopo-projeto-assinatura.md"
  - "wiki/features/secretaria/secretaria-ai-gabi.md"
  - "wiki/features/marcelle/automacao-notificacao-marcelle.md"
  - "wiki/outputs/relatorio-entregas-valor-agregado-2026-05-14.md"
created: 2026-05-14
updated: 2026-05-15
revisions:
  - "2026-05-14: versão inicial com 5 seções (diagnóstico, cronograma, escopo Marcelle, financeiro, aceite)"
  - "2026-05-15: incorporadas considerações de Gustavo — cronograma esclarecido (Marcelle inicia execução no Mês 2), política de parcelas definida (recorrente + aceite como condição de continuidade), escopo Marcelle refinado, critérios de aceite operacionais"
---

# Revisão Contratual — Escopo, Cronograma, Financeiro e Aceite

## Objetivo

Minuta técnica/comercial para alinhamento contratual com a Assinatura Marca Própria. Não substitui o contrato jurídico — serve como instrumento de gestão para transformar contrato e calendário em itens verificáveis. Cobre cinco pontos críticos: diagnóstico das duas frentes, cronograma, escopo objetivo da Marcelle, estrutura financeira de continuidade e critérios de aceite dos MVPs.

---

## Resumo executivo (responde às 5 considerações)

| # | Consideração | Posição registrada neste documento |
|---|---|---|
| 1 | **Diagnóstico** — Gabi completo, Marcelle ainda pendente | Documentado como tal. Marcelle terá Mês 1 dedicado a diagnóstico operacional completo antes de execução técnica vinculada a entregas. |
| 2 | **Cronograma** — paralelo ou sequencial? | **Híbrido:** Mês 1 = Gabi em execução + Marcelle em diagnóstico/preparação. **Marcelle "começa de verdade" no Mês 2**, em paralelo à Gabi, reaproveitando a base técnica já construída. |
| 3 | **Escopo Marcelle** — o que está incluído de fato? | Lista objetiva em 3 grupos: (a) **incluído** (base Asana, consulta de status, reports internos básicos, agente reativo via WhatsApp); (b) **condicionado ao diagnóstico** (visualizações estruturadas internas/cliente, reports avançados); (c) **fora do escopo / nova fase** (dashboard unificado, portal cliente, BI). |
| 4 | **Estrutura financeira** — valor por fase, gatilho de parcela, entrega vinculada | **Parcelas recorrentes via Mercado Pago** (R$ 1.200/mês Gabi + R$ 1.000/mês Marcelle, 10 parcelas cada). **Aceite do MVP do mês anterior é condição de continuidade** — se não houver aceite, ciclo seguinte fica formalmente suspenso até resolução. Cada parcela está vinculada a entregas específicas (tabela em §4). |
| 5 | **Critério de aceite dos MVPs** | MVP é entregue quando o fluxo principal está funcional, foi enviado para teste com instrução de uso e validado pela responsável operacional (Gabi para Gabi, Marcelle para Marcelle). Prazo de retorno: **3 dias úteis**. Ausência de retorno = aceite operacional para continuidade. Bloqueadores impedem aceite; médios/baixos viram backlog. |

---

# 1. Diagnóstico — status por frente

> **⚠️ Frente Marcelle: diagnóstico ainda PENDENTE.** O escopo fino e os critérios de aceite específicos da automação Marcelle dependem de uma sessão de diagnóstico operacional com Marcelle, prevista para acontecer no decorrer do Mês 1.

## Situação atual

| Frente | Status do diagnóstico | Base atual |
|---|---|---|
| **Gabi — Secretária A.I. + Designer** | ✅ Mais completo, validado operacionalmente | Sessão presencial realizada (24/03). Dores, fluxos e MVPs mapeados com precisão. Execução em andamento desde Semana 1. |
| **Marcelle — Automação de Projetos** | ⏳ Parcial, pendente de fechamento | Existe levantamento indireto via Asana e entendimento inicial do fluxo. **Falta diagnóstico operacional direto com Marcelle** para fechar escopo fino e critérios. |

## Consequência operacional

- Frente Gabi segue com execução e validação dos MVPs já definidos.
- Frente Marcelle entra como **escopo progressivo**: Mês 1 dedicado a diagnóstico + preparação técnica; Meses 2–4 dedicados à execução vinculada a entregas.
- Qualquer expansão relevante da Marcelle após o diagnóstico (que ultrapasse os "incluídos" da §3) é registrada como **ajuste de escopo** ou **nova fase contratual**.

## Redação contratual sugerida

> O diagnóstico da frente Gabi encontra-se completo, com fluxos principais e MVPs definidos e em execução. A frente Marcelle encontra-se com diagnóstico parcial, baseado em análise indireta do Asana, e depende de validação operacional complementar com Marcelle (a ser realizada no Mês 1) para fechamento de escopo, priorização e critérios de aceite específicos. Itens marcados como "condicionados ao diagnóstico" no escopo da Marcelle ficam pendentes desta validação.

---

# 2. Cronograma — paralelo ou sequencial?

## Conclusão direta

> **As duas frentes correm dentro do mesmo ciclo contratual de 4 meses, mas com modelos de execução diferentes:**
>
> - **Gabi:** execução técnica desde o Mês 1.
> - **Marcelle:** **Mês 1 é diagnóstico + preparação** (não há entrega técnica vinculada). **Execução técnica real começa no Mês 2**, em paralelo à Gabi, reaproveitando a base já construída.
>
> Não é "Marcelle só começa quando Gabi terminar". É "Marcelle só executa quando há base diagnóstico + técnica para isso, o que acontece a partir do Mês 2".

## Cronograma macro

| Mês | Período | Gabi — execução técnica | Marcelle — execução técnica | Observação |
|---|---|---|---|---|
| **Mês 1** | 24/03–21/04 | Auto-reply WhatsApp + base Bot Gabi | **Diagnóstico operacional + preparação base Asana** | Marcelle: levantamento, não há MVP técnico ainda. Gabi: MVP 1 já entregue. |
| **Mês 2** | 22/04–19/05 | Atas no Asana + início de testes Secretária A.I. | **Início real — agente reativo + reports internos básicos** | Ambas frentes executando. Marcelle usa base Bot Gabi (WhatsApp/Asana/Redis/Postgres). |
| **Mês 3** | 20/05–16/06 | Gerador de imagens/apresentações (Designer) em teste | Ajustes pós-teste + refinamento de reports/status | Evolução paralela após validação operacional dos dois. |
| **Mês 4** | 17/06–14/07 | Validação final + lançamento | Estabilização + documentação operacional | Fechamento das duas frentes. |

## Dependência técnica explícita

A base técnica compartilhada (WhatsApp via Evolution, Asana API, Redis, PostgreSQL, FastAPI) é construída no Mês 1 para a Secretária A.I. da Gabi. A automação da Marcelle reaproveita essa mesma base — por isso:

- não há retrabalho de infraestrutura;
- não há custo extra de hospedagem para Marcelle (cliente paga 1× a infra);
- a execução técnica da Marcelle é mais rápida (Meses 2–4) porque a base já existe.

## Redação contratual sugerida

> O projeto possui duas frentes dentro do mesmo período contratual de 4 meses: Secretária A.I. da Gabi e Automação de Projetos da Marcelle. A execução é integrada via infraestrutura compartilhada. A frente Gabi executa entregas técnicas desde o Mês 1. A frente Marcelle dedica o Mês 1 ao diagnóstico operacional e preparação técnica, e inicia execução vinculada a entregas a partir do Mês 2, em paralelo à Gabi. Esta estrutura reduz retrabalho e custo de infraestrutura, ao mesmo tempo que garante diagnóstico adequado antes de execução da segunda frente.

---

# 3. Escopo objetivo da Marcelle

> Para evitar ambiguidade, o escopo da Marcelle é registrado em **3 grupos**: incluído no contrato atual, condicionado ao diagnóstico do Mês 1, e fora do escopo atual.

## 3.1. ✅ Incluído no escopo atual (contratado)

| Item | Descrição | Onde executa |
|---|---|---|
| Base Asana organizada | Estrutura inicial para leitura dos projetos, etapas e dados necessários para automação. | Mês 1 (preparação) |
| Estrutura de dados operacional | Banco para armazenar/consultar informações de projetos e status, reaproveitando Postgres existente. | Mês 1 (preparação) |
| Consulta de status de projetos | Permitir entender em que etapa cada projeto está, via consulta natural (texto/WhatsApp). | Mês 2 |
| Reports internos básicos | Alertas e resumos sobre atrasos, pendências e inconsistências com base nos dados disponíveis no Asana. | Mês 2 |
| Agente reativo para consulta | Marcelle pergunta sobre um projeto/status no WhatsApp e recebe resposta baseada nos dados. | Mês 2 |
| WhatsApp como canal operacional | Uso do WhatsApp (via Evolution API já em produção) como canal de consulta, alertas e respostas. | Mês 2 |

## 3.2. ⏳ Condicionado ao diagnóstico do Mês 1

| Item | Condição para inclusão |
|---|---|
| Visualização interna estruturada | Diagnóstico precisa definir: quais indicadores Marcelle quer ver, com que frequência, e quais dados existem no Asana hoje. |
| Visualização para cliente | Diagnóstico precisa definir: nível de exposição, linguagem, permissões e formato de entrega (PDF? Link? Dashboard simples? Mensagem WhatsApp?). |
| Reports avançados (proativos) | Diagnóstico precisa definir critérios de atraso/erro/status — quando o sistema dispara o alerta sem ser perguntado. |
| Fluxos automáticos por etapa | Diagnóstico precisa mapear quais etapas do projeto disparam ações automáticas. |

> Itens desta categoria entram em escopo **após o diagnóstico do Mês 1 confirmá-los como viáveis e prioritários**. Se confirmados, são executados nos Meses 2–4 dentro da parcela mensal. Se ultrapassarem capacidade do ciclo, viram aditivo.

## 3.3. ❌ Fora do escopo atual (nova fase ou aditivo)

| Item | Motivo |
|---|---|
| Dashboard unificado completo | Exige UX dedicada, sistema de permissões, layout, indicadores definidos, telas e revisão de valor. Não cabe no ciclo de 4 meses. |
| Portal completo para cliente | Exige produto separado, autenticação, gestão de permissões e definição de experiência externa do cliente. |
| BI completo / analytics avançado | Exige modelagem analítica dedicada, ETL, ferramentas dedicadas. Escopo de produto à parte. |

## Redação contratual sugerida

> O escopo atual da Automação Marcelle inclui: estruturação da base de projetos no Asana, banco de dados operacional, consulta de status de projetos, reports internos básicos, agente reativo via WhatsApp e uso do WhatsApp como canal operacional. Visualizações estruturadas (interna ou cliente), reports avançados proativos e fluxos automáticos por etapa do projeto fazem parte de uma camada **condicionada ao diagnóstico do Mês 1** — confirmados após validação operacional com Marcelle, entram em execução nos Meses 2–4. Dashboard unificado completo, portal para cliente e BI avançado **não estão incluídos no escopo atual** e devem ser tratados como nova fase contratual ou aditivo.

---

# 4. Estrutura financeira da continuidade

## Modelo contratado

| Frente | Valor mensal | Total | Forma | Canal |
|---|---:|---:|---|---|
| Gabi — Secretária A.I. + Designer | R$ 1.200 | 10 parcelas | Recorrência mensal | Mercado Pago |
| Marcelle — Automação de Projetos | R$ 1.000 | 10 parcelas | Recorrência mensal | Mercado Pago |

> Juros, formato exato da recorrência e número final de parcelas confirmados com gerente do Mercado Pago. **Ponto pendente:** documentação interna ainda precisa anexar o termo formal do Mercado Pago.

## Gatilho de continuidade (política definida)

> **Parcelas correm via recorrência Mercado Pago, mas o aceite do MVP do mês anterior é condição de continuidade contratual.**
>
> Se o MVP de um mês **não for aceito** (ver §5), o ciclo seguinte fica **formalmente suspenso** até resolução — a parcela seguinte é interrompida da recorrência (via Mercado Pago) e a contagem do cronograma é congelada. Bloqueadores resolvidos retomam o ciclo.

Isto equilibra duas necessidades:

- **Fluxo de caixa:** parcelas mensais previsíveis pela recorrência automática, sem fricção de cobrança ciclo a ciclo.
- **Accountability:** entregar mal não é remunerado, e a cliente tem garantia de que o pagamento está conectado a entrega real.

## Vinculação parcela ↔ entrega (Gabi)

| Parcela (mês) | Período | Entrega vinculada (MVP) | Aceite condição-para |
|---|---|---|---|
| Parcela Mês 1 | 24/03–21/04 | **MVP 1:** Auto-reply WhatsApp + setup Bot Gabi | Liberação da Parcela 2 |
| Parcela Mês 2 | 22/04–19/05 | **MVP 2:** Atas processadas e enviadas ao Asana | Liberação da Parcela 3 |
| Parcela Mês 3 | 20/05–16/06 | **MVP 3:** Designer (gerador de imagens/apresentações) em teste | Liberação da Parcela 4 |
| Parcela Mês 4 | 17/06–14/07 | **MVP 4:** Validação final + lançamento da Secretária A.I. + Designer | Encerramento do ciclo |

## Vinculação parcela ↔ entrega (Marcelle)

| Parcela (mês) | Período | Entrega vinculada | Aceite condição-para |
|---|---|---|---|
| Parcela Mês 1 | 24/03–21/04 | **Marco de diagnóstico:** sessão de diagnóstico operacional realizada + base Asana estruturada + escopo dos itens "condicionados" definido | Liberação da Parcela 2 |
| Parcela Mês 2 | 22/04–19/05 | **MVP 1:** Agente reativo via WhatsApp respondendo a consultas de status + reports internos básicos funcionando | Liberação da Parcela 3 |
| Parcela Mês 3 | 20/05–16/06 | **MVP 2:** Ajustes pós-teste + reports/status refinados conforme uso real | Liberação da Parcela 4 |
| Parcela Mês 4 | 17/06–14/07 | **MVP 3:** Estabilização operacional + documentação | Encerramento do ciclo |

> **Nota importante** sobre Marcelle Mês 1: a entrega vinculada é o **marco de diagnóstico**, não um MVP técnico. Isso reflete a realidade de que Marcelle precisa de sessão diagnóstica antes de execução. O aceite do diagnóstico (escopo dos itens condicionados, validação da base Asana, plano de execução Meses 2–4) libera a Parcela 2.

## Redação contratual sugerida

> A contratação prevê pagamento mensal recorrente via Mercado Pago: R$ 1.200/mês para a frente Gabi (10 parcelas) e R$ 1.000/mês para a frente Marcelle (10 parcelas). Cada parcela mensal está vinculada a uma entrega específica do mês correspondente. O aceite formal da entrega do mês anterior é **condição de continuidade**: ausência de aceite (ou bloqueador crítico não resolvido) suspende a recorrência da parcela seguinte até resolução. Esta política não impede pagamentos atrasados ou retomadas; serve apenas para garantir vinculação entre pagamento e entrega.

---

# 5. Critério de aceite dos MVPs

## Estados de um MVP

| Estado | Significado |
|---|---|
| Em desenvolvimento | Implementação em andamento. |
| Pronto para teste | Entrega funcional disponível para validação. |
| Em validação | Responsável operacional testando e retornando ajustes. |
| Aceito com ajustes | MVP aprovado para uso, com melhorias menores registradas em backlog. |
| Aceito | MVP validado e considerado entregue. |
| Reaberto | Problema crítico encontrado após aceite — bloqueia ciclo seguinte até resolução. |

## Definição operacional

**Um MVP é considerado pronto para teste quando:**

- ✅ Fluxo principal está implementado e executando ponta a ponta.
- ✅ Dependências essenciais (APIs, integrações, dados) estão configuradas.
- ✅ Teste interno básico foi realizado pelo time de desenvolvimento.
- ✅ Erros críticos conhecidos estão documentados (lista visível para a responsável).
- ✅ Instrução de uso/validação foi enviada para a responsável operacional.

**Um MVP é considerado aceito quando:**

- ✅ A responsável operacional validou que o fluxo principal funciona no cenário real.
- ✅ Bugs críticos bloqueadores foram resolvidos ou formalmente registrados como pendência aceita.
- ✅ Ajustes menores estão listados como backlog (não bloqueiam o aceite).
- ✅ O aceite foi registrado na KB / no calendário / por e-mail ou WhatsApp formal.

## Quem valida

| Frente | Validador operacional | Aceite executivo (se aplicável) |
|---|---|---|
| Gabi — Secretária A.I. | **Gabi** (uso diário do bot) | Amanda (impacto / continuidade contratual) |
| Designer Gabi | **Gabi** (fluxo de criação/edição de peças) | Amanda (padrão de entrega visual) |
| Marcelle — Automação Projetos | **Marcelle** (uso operacional dos reports/consultas) | Amanda (alinhamento estratégico / continuidade) |

## Prazo de retorno

> **3 dias úteis** após envio do MVP para validação. Ausência de retorno dentro do prazo caracteriza **aceite operacional tácito** para fins de continuidade do cronograma. Melhorias e ajustes não bloqueadores podem ser registrados em backlog posteriormente, mas não voltam ao status de bloqueio.

Exceções:

- **Bloqueador descoberto após aceite tácito** (até 5 dias úteis após): reabertura permitida com justificativa.
- **Indisponibilidade da responsável** (viagem, doença, evento): o prazo pode ser estendido por acordo formal antes do vencimento.

## Classificação de ajustes

| Severidade | Definição | Impacto no aceite |
|---|---|---|
| **Bloqueador** | Impede uso do fluxo principal. | MVP **não aceito** até correção ou decisão explícita. Suspende parcela seguinte. |
| **Alto** | Afeta uso relevante, mas há workaround. | Aceito **com ajuste obrigatório** em curto prazo (até 5 dias úteis). |
| **Médio** | Melhoria importante, não impede uso. | Vai para **backlog do próximo ciclo**. Não bloqueia aceite. |
| **Baixo** | Ajuste cosmético ou preferência. | **Backlog**. Não bloqueia aceite. |

## Redação contratual sugerida

> Cada MVP será enviado para validação da responsável operacional da frente correspondente (Gabi para Secretária A.I. e Designer; Marcelle para Automação de Projetos), acompanhado de instrução de uso. A entrega será considerada aceita quando o fluxo principal puder ser executado no cenário real ou quando eventuais ajustes remanescentes forem classificados como não bloqueadores (médios/baixos). O prazo de retorno é de até 3 dias úteis após envio para teste. Ausência de retorno dentro do prazo caracteriza aceite operacional para continuidade do cronograma. Bugs bloqueadores impedem o aceite e suspendem a parcela do ciclo seguinte até resolução, conforme política financeira (§4).

---

# Próximos passos antes da apresentação à Assinatura

1. **Confirmar com Mercado Pago** o termo formal de recorrência: número de parcelas, juros, possibilidade de suspensão por ciclo.
2. **Agendar diagnóstico operacional com Marcelle** dentro do Mês 1 — sessão dedicada, com agenda fechada (escopo, indicadores desejados, prioridades, dados disponíveis).
3. **Validar este documento com Lucas** (sócio Tzolkin) antes de levar à Assinatura.
4. **Apresentar à Amanda** como instrumento de gestão contratual (não como adendo jurídico).
5. **Anexar ao Notion** na página principal do contrato (`collection://3532551e-c67e-8085-8ba8-000bc271621a`) e marcar revisão na Semana 5.

---

## Relacionados

- [Escopo Projeto Assinatura](../workflows/escopo-projeto-assinatura.md)
- [Secretaria A.I. Gabi](../features/secretaria/secretaria-ai-gabi.md)
- [Automação Notificação Marcelle](../features/marcelle/automacao-notificacao-marcelle.md)
- [Relatório Entregas Valor Agregado 2026-05-14](relatorio-entregas-valor-agregado-2026-05-14.md)
- [Timeline Calendário Obsidian 2026-04-01 a 2026-05-14](timeline-calendario-obsidian-2026-04-01-2026-05-14.md)
