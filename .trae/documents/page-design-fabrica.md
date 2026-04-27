# Page Design — Novo fluxo da Fábrica

## 1) Diretrizes globais (desktop-first)

### Layout
- Base: CSS Grid para estrutura + Flexbox para alinhamentos internos.
- Container desktop: 1200–1440px (gutter consistente). Em telas grandes, usar layout “editor”.
- Breakpoints: Desktop 1024px+; Tablet 768–1023px; Mobile <768px.

### Meta Information
- Title (Home): "Assinatura — Início"
- Title (Fábrica): "Assinatura — Fábrica"
- Description: resumo curto do objetivo da página.
- Open Graph: título + descrição + URL + imagem padrão.

### Global Styles (tokens)
- Background neutro claro; Cards/surfaces brancos.
- Accent primário da marca; hover com leve elevação; disabled com opacidade.
- Tipografia 14–16px base; títulos 20/24/32px.

---

## 2) Página Inicial

### Page Structure
- Coluna única com header simples + card de entrada.

### Seções & Componentes
1. Header: logo/nome do produto + CTA/link “Fábrica”.
2. Card “Fábrica”: descrição curta + botão “Abrir Fábrica”.

---

## 3) Página Fábrica (novo fluxo)

### Objetivo
- Você entra, vê uma **animação inicial**, escolhe **Imagem / Apresentação / Animação** e configura tudo em uma **tela única por tipo** (sem wizard procedural entre etapas).

### Page Structure (desktop-first)
- A página tem **2 estados de UI** dentro do mesmo route (/fabrica):
  1) **Estado A — Intro/Escolha do tipo**
  2) **Estado B — Configuração do tipo selecionado**

### Estado A — Intro/Escolha do tipo
- Layout: centro da tela (Grid 12 col) com bloco principal centralizado.
- Componentes:
  1. **Animação inicial** (lottie/video/ilustração animada): 4–8s, loop suave; pode reduzir/pausar após a primeira execução.
  2. Título + subtítulo: “O que você vai criar hoje?”
  3. **Cards de escolha** (3 cards iguais):
     - Card “Imagem” (ícone + 1 linha de descrição)
     - Card “Apresentação”
     - Card “Animação”
     - Interação: clique seleciona e transiciona para o Estado B.

### Estado B — Configuração específica por tipo (tela única)
- Layout “editor” em 3 painéis:
  - Esquerda (Estrutura/Layouts/Templates quando aplicável): ~22–26%
  - Centro (Canvas/Preview): ~48–56%
  - Direita (Brief/Brand/Configurações + Gerar): ~22–26%
- Top bar:
  1. Título “Fábrica”
  2. Indicador do tipo atual (ex.: “Tipo: Apresentação”)
  3. Ação “Trocar tipo” (volta ao Estado A)

#### Coluna Esquerda (condicional por tipo)
- Quando tipo=**Apresentação**:
  - Estrutura: lista de slides/cards + reordenação quando aplicável.
  - Templates: galeria de templates.
  - Layouts (ícones): biblioteca de layouts atômicos.
- Quando tipo=**Imagem** ou **Animação**:
  - Mostrar apenas o que fizer sentido (ex.: Layouts se suportado), sem forçar estrutura de slides.

#### Coluna Central — Preview pré-geração
- Canvas na proporção do preset escolhido.
- Badge/Barra: dimensões (L×A) + toggle “Safe-area”.
- Safe-area: overlay visual apenas para orientação.

#### Coluna Direita — Configuração (sem wizard)
- Card “Brief/Prompt”: campos guiados + campo livre (raw) quando existir.
- Card “Brand Kit / Fontes”: upload + seletores (títulos/corpo) + aviso de fallback.
- Card “Configurações”: apenas dropdowns/toggles/presets (evitar números livres).
- Ação principal: botão **“Gerar”** sticky no rodapé.

### Interações e estados
- Transição A→B: animação rápida (200–300ms) + foco no preview.
- “Trocar tipo”: volta para A (com aviso se houver configurações não salvas, quando aplicável).
- Loading ao gerar: botão em loading + canvas com skeleton mantendo dimensões/safe-area.

### Responsivo
- Tablet/Mobile: colapsar para stack (Tipo/Config → Preview → Gerar), mantendo dimensões visíveis no preview.