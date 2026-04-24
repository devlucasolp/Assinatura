### 1. Automação de Notificação (Asana)

**Prazo Total:** 1 Mês (4 Semanas) | **Frequência de Testes:** 1 MVP por semana

Como o prazo é de um mês e exige validações semanais, o ideal é dividir as features (funcionalidades) em ciclos curtos de entrega para garantir que cada teste tenha um foco específico.

- **Semana 1: Infraestrutura e Dados**
    - **Desenvolvimento:** Estruturação do ERMs interno.
    - **Entrega:** MVP 1 (Teste da base de dados e integração inicial).
- **Semana 2: Lógica de Negócio**
    - **Desenvolvimento:** Implementação do cálculo e estimativa de tempo operacional.
    - **Entrega:** MVP 2 (Teste das regras de cálculo e precisão do tempo).
- **Semana 3: Visualização**
    - **Desenvolvimento:** Criação dos Reports internos.
    - **Entrega:** MVP 3 (Teste da geração de relatórios com dados reais).
- **Semana 4: Polimento e Lançamento**
    - **Desenvolvimento:** Correção de bugs, refinamento do sistema e validação final de todas as features conectadas.
    - **Entrega:** MVP 4 / Lançamento (Teste final do fluxo completo) e entrega oficial do projeto.

---

### 2. Secretaria A.i (Gabi)

**Prazo Total:** 4 Meses (Aprox. 16 Semanas) | **Frequência de Testes:** 1 MVP por mês

Este é um projeto mais longo e robusto. A divisão foi feita agrupando as features por similaridade técnica, garantindo um MVP funcional ao final de cada mês (a cada 4 semanas).

- **Mês 1 (Semanas 1 a 4): Comunicação e Agendamento**
    - **Desenvolvimento:** Integração de Tasks via WhatsApp (WPP) e Automatização da agenda Google.
    - **Entrega:** MVP 1 (Teste do fluxo de receber tarefas pelo WhatsApp e refleti-las na agenda).
- **Mês 2 (Semanas 5 a 8): Automação de Respostas e Follow-up**
    - **Desenvolvimento:** Configuração de Respostas Automáticas e sistema de Lembretes de tarefas.
    - **Entrega:** MVP 2 (Teste da Gabi interagindo automaticamente e enviando alertas de prazos).
- **Mês 3 (Semanas 9 a 12): Gestão de Documentos**
    - **Desenvolvimento:** Automação de envio de documentos para o Google Drive.
    - **Entrega:** MVP 3 (Teste do recebimento de arquivos e organização automática nas pastas corretas).
- **Mês 4 (Semanas 13 a 16): Geração de Ativos e Entrega Final**
    - **Desenvolvimento:** Automação com gerador de Apresentações e Artes. Revisão de todos os módulos.
    - **Entrega:** MVP 4 (Teste da geração de materiais visuais) e Lançamento oficial da versão completa.

---

### Lembrete de Gestão

- **Ação Pendente:** Confirmar com o gerente do Mercado Pago os juros e o número exato de parcelas para os valores em Gateway (1.000/mo x10 para o Asana e 1.200/mo x10 para a Gabi).

---

```mermaid
gantt
    title Cronograma de Projetos - Visualizacao Limpa
    dateFormat YYYY-MM-DD
    axisFormat %d/%m

    section Asana 1 Mes
    Semana 1 ERMs e Dados :a1, 2026-03-24, 7d
    MVP 1 Asana :milestone, m1, 2026-03-31, 0d
    Semana 2 Logica e Calculo :a2, after m1, 7d
    MVP 2 Asana :milestone, m2, 2026-04-07, 0d
    Semana 3 Reports :a3, after m2, 7d
    MVP 3 Asana :milestone, m3, 2026-04-14, 0d
    Semana 4 Entrega :a4, after m3, 7d
    Entrega Final Asana :milestone, m4, 2026-04-21, 0d

    section Gabi 4 Meses
    Mes 1 Tasks WPP e Agenda :g1, 2026-03-24, 28d
    MVP 1 Gabi :milestone, mg1, 2026-04-21, 0d
    Mes 2 Respostas e Lembretes :g2, after mg1, 28d
    MVP 2 Gabi :milestone, mg2, 2026-05-19, 0d
    Mes 3 Docs no Drive :g3, after mg2, 28d
    MVP 3 Gabi :milestone, mg3, 2026-06-16, 0d
    Mes 4 Artes e Apresentacoes :g4, after mg3, 28d
    Lancamento Final Gabi :milestone, mg4, 2026-07-14, 0d
```