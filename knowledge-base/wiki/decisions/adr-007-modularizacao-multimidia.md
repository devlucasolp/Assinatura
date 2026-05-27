# ADR 007: Modularização Multimídia e Estrutura Orientada a Classes

## Data
2026-05-24

## Status
Aceito e Parcialmente Implementado (Fase 1 e Refatorações Base)

## Contexto
Atualmente, o pipeline de geração de design (`routes/ai.ts` e `agents/pipeline.ts`) é altamente acoplado ao formato de "Apresentação" (16:9) e "Carrossel" (1:1). As lógicas de cálculo de posicionamento (Layout Engine), hierarquia visual e tipografia estão misturadas em funções procedurais, o que dificulta a escalabilidade.
Com a necessidade de suportar novos formatos no futuro próximo — como **Instagram Posts (Stories/Reels 9:16)**, **TikTok** e **Animações** —, manter o código acoplado resultará em duplicação de lógica e difícil manutenção. Além disso, o usuário apontou a necessidade de ajustes finos constantes na tipografia e hierarquia visual, que exigem uma estrutura mais robusta.

## Decisão
Decidimos refatorar o motor de geração de design para uma **arquitetura modular orientada a classes** (Strategy/Factory Patterns), permitindo o reuso e a especialização para múltiplas mídias:

1. **Format Strategies:** Criar classes base (ex: `MediaStrategy`, `PresentationStrategy`, `SocialMediaStrategy`) que definem proporções, zonas seguras e regras específicas de layout.
2. **Layout Engines Modulares:** Separar a lógica de cálculo de (X,Y, W, H) e quebra de linhas (`estimateTextHeight`) em classes independentes de Layout Engine.
3. **Typography Manager:** Centralizar regras de hierarquia visual (eyebrow, headline, body), pesos e escalas de fonte em um módulo reciclável, garantindo contraste automático (ex: `contrastBackground=true` para imagens full-bleed).
4. **Animation Controller:** Preparar o terreno para injeção de propriedades de animação (`animationIn`, `animationDelay`, `animationDuration`) nos elementos gerados, delegando a execução para o frontend (CanvasEditor).
5. **Integração:** Manter o `DesignDocument` como formato semântico universal transitando entre o Agente Cérebro e o Renderer/Editor, agnóstico à mídia final até o momento da compilação.

## Consequências
- **Positivas:** 
  - Facilidade em plugar novos formatos (ex: instanciar `new TikTokStrategy()`).
  - Lógica de hierarquia visual (espaçamentos, sobreposições) centralizada, evitando os problemas atuais de textos sobrepostos.
  - Código limpo, testável e sem funções "god" com milhares de linhas.
- **Negativas:** 
  - Necessidade de refatorar as funções existentes (`zoneToLayer`, `generateTextLayers`) para o novo padrão.
  - Curva de aprendizado ligeiramente maior para entender a injeção de dependências das estratégias de mídia.

## Atualizações de Implementação (2026-05-25)
- O código sofreu uma extensa limpeza seguindo princípios de **Object Calisthenics** (substituição massiva de declarações `else` por Early Returns e guard clauses).
- A **Layout Engine** (`zoneToLayer` em `agents/design/index.ts`) já foi refatorada e unificada em um Strategy Pattern (`layoutStrategies`) que gerencia a distribuição dos elementos com base no template, sem encadeamento de `if/else`.
- Implementou-se regras de design system rígidas no `agents/planner/index.ts`: obrigatoriedade de fundo branco/texto preto em templates de conteúdo denso, proibição de solicitação de textos embutidos no `imageHint` (verificado pelo `reviewer/index.ts`), e liberdade total de exploração de formas decorativas.
