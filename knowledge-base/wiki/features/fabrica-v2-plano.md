# Plano de Implementação: Fábrica v2 (Modular & Híbrida)

Este documento substitui o antigo `fabrica-checklist.md` (legado) e reflete a arquitetura correta: **Agente Cérebro → DesignDocument → CanvasEditor Nativo (Sem Canva)**, além da modularização futura para multimídia (ADR-007).

## 1. Ajuste Fino de Tipografias e Hierarquia Visual (Fase Atual)

Baseado no feedback (`feedback-ajuste-fino-geracao-primordial.md`), as seguintes regras foram/estão sendo aplicadas no motor de layout:
- [x] **Layout Engine Inteligente:** Templates definem o macro-layout (split, full-bleed) e a engine respeita as intenções.
- [x] **Cálculo de Quebra de Linhas:** Evitar sobreposições calculando a altura real do texto.
- [x] **Hierarquia Rigorosa:** 
  - Eyebrow: pequeno, caps.
  - Headline: grande, bold.
  - Body: lineHeight 1.6.
- [x] **Contraste Dinâmico:** Aplicação de overlay (`contrastBackground`) em templates full-bleed.
- [ ] **Typography Manager:** Extrair essas regras hardcoded para uma classe de gerência tipográfica reutilizável (Refatoração Pendente).

## 2. Refatoração Modular (ADR-007)

Preparação do terreno para Instagram, TikTok e Animações:
- [ ] **Criar Abstrações de Mídia:** Desenvolver interfaces `IMediaStrategy` para abstrair `Presentation`, `Carousel`, `Stories`, etc.
- [ ] **Extração do Layout Engine:** Transformar a função `zoneToLayer` em uma classe `LayoutEngine` injetável.
- [ ] **Separação de Preocupações:** Quebrar o arquivo `routes/ai.ts` e `agents/design/index.ts` em módulos menores e testáveis.

## 3. Arquitetura Conversacional (Cérebro)

- [x] **Contexto e Memória:** Histórico de chat preservado com a arte (`chatHistory`).
- [x] **Suporte a Anexos:** Imagens enviadas pelo usuário entram como referências reais.
- [x] **Edições Fluídas:** Cérebro religa o pipeline (`[DISPATCH:...]`) com o brief completo reconstruído após pedido de alteração.
- [ ] **Pesquisa e Bench Automático:** Permitir ao Cérebro buscar referências ativamente antes de iniciar o planejamento.

## 4. Evolução do CanvasEditor (Frontend)

- [x] **Visualização de Preview:** Layout `mode="cover"` perfeito no index do editor.
- [x] **Animações (Base):** Suporte a `animationIn` implementado via CSS Keyframes no renderer.
- [ ] **Timeline/Controles Sociais:** Adicionar UI para controle de tempo de animações (útil para TikTok/Reels futuramente).
