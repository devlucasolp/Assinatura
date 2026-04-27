# Benchmarking (Canva / Figma / Beautiful.ai / Gamma / Pitch / Slidebean) + Proposta de layout da Fábrica

## Objetivo

Você pediu para “pesquisar direito” como ferramentas de criação (principalmente para **apresentações/carrosséis**) organizam **prompt + configurações** e como mostram **dimensões no preview antes de gerar**.

Também atende a diretriz de produto: **sem chat** (o fluxo é template/preset-first, não conversa).

## Critérios usados no benchmarking

1) **Fluxo de entrada**: template-first vs outline-first vs smart-layout.
2) **Guardrails**: o quanto dá pra errar (ex.: quebrar alinhamento/spacing) vs “bom por padrão”.
3) **Brand kit**: fontes/cores/logo e reaplicação rápida.
4) **Editor**: 3 painéis (biblioteca/outline, canvas, inspector) e consistência de interação.
5) **Prévia**: dimensão, proporção, safe area e validação antes de exportar/gerar.
6) **Export**: o caminho natural do usuário (PDF/PPTX/link/video).

---

## Benchmarking por padrão de ferramenta

### 1) Canva (template-first, não-designers)

**Padrão de UI**
- Sidebar esquerda com “biblioteca” (templates, elementos, uploads etc.) + canvas central + barra superior contextual. Isso reduz o custo cognitivo e “organiza por intenção”.[^1]
- Brand kit e estilos aparecem como aplicação rápida de fontes/cores/logos dentro do editor (um clique para aplicar).[^2]

**O que copiar pra Fábrica**
- Fluxo “começar por template/preset”, depois substituir conteúdo.
- Biblioteca de blocos e assets (drag-and-drop) separada do painel de propriedades.

**Risco a evitar**
- Excesso de opções “numéricas” soltas (grid columns, etc.) tende a virar ruído. Canva entrega poder por meio de *presets* e menus contextuais, não por um painel gigante de números.

### 2) Beautiful.ai (smart layout / guardrails fortes)

**Padrão de produto**
- “Smart Slides” (templates inteligentes) que **auto-reorganizam** conteúdo (alinhamento/spacing) enquanto você edita, reduzindo o trabalho manual de “nudge”.[^3]

**O que copiar pra Fábrica**
- Guardrails como *default*: você edita conteúdo + escolhe layout, e o sistema mantém consistência.
- Configs em forma de **escolhas discretas** (layout/variação) em vez de dezenas de sliders.

### 3) Pitch (slides colaborativos + biblioteca de layouts)

**Padrão de produto**
- Forte em “templates + layouts”: você escolhe template e vai adicionando slides/estruturas (timelines, image grids etc.).[^4]
- Tem modelo de “style builder/slide style” para garantir consistência de cor/fonte e aplicação em slides.[^5]

**O que copiar pra Fábrica**
- Separar “estilo do deck” (brand/style) do conteúdo de cada slide.
- Biblioteca de layouts por slide, sempre coerente com o tema/estilo selecionado.

### 4) Gamma (outline-first + configurações antes de gerar)

**Padrão de produto**
- Antes de gerar, o usuário escolhe parâmetros como **número de cards**, estilo/tema e outros ajustes de conteúdo/imagens.[^6]
- Editor tende a usar filme-strip/outline à esquerda e edição do card no centro (padrão “outline → refine”).[^6]

**O que copiar pra Fábrica**
- Um passo explícito “Configurar antes de gerar” com preview de dimensão e densidade.
- Controles tipo “Text amount: brief/medium/detailed” (controle real de resultado, não *micro controles* irreais).

### 5) Slidebean (pitch decks, IA para arranjo)

**Padrão de produto**
- Separa “conteúdo” de “design”: você preenche e a IA reorganiza/arranja visualmente (“arrange with AI”).[^7]

**O que copiar pra Fábrica**
- Botão “Reorganizar layout” como ação segura (não exige que a Gabi vire designer de grid).

### 6) PowerPoint/Copilot (baseline do mercado)

**Padrão de produto**
- O mercado já educou usuários a pensar em: outline → sugestões de layout → export/compartilhar.
- Copilot reforça o padrão “sugerir fluxo/estrutura” e “layout suggestions”.[^8]

---

## Síntese do benchmarking (o que funciona mesmo)

**Padrões que se repetem entre os melhores**
1) **3 painéis**: biblioteca/outline (esq.) + canvas (centro) + inspector (dir.).
2) **Presets em vez de infinitos números**: escolhas discretas (layout, densidade, tema, estilo de imagem).
3) **Config antes de gerar**: tamanho/formato/densidade claros *antes* do “Gerar”.[^6]
4) **Guardrails por layout**: smart templates (Beautiful.ai) ou arrange-with-AI (Slidebean) para consistência.[^3][^7]
5) **Brand kit separado**: estilos do projeto (cores/fontes/logo) ficam num nível acima dos slides.[^2][^5]

---

## Proposta de layout “certo” para a Fábrica (sem chat)

### Objetivo

Juntar **brief/prompt + configurações realistas** no mesmo lugar, por tipo de conteúdo, e dar para a Gabi **prévia de tamanho + safe-area** antes de gastar geração.

### Estrutura recomendada (bem próxima do padrão Canva/Pitch)

1) **Top bar**
- Tipo de conteúdo: **Apresentação / Imagem / Animação**
- Preset de formato: ex.: `Instagram Carrossel 1080×1080`, `Story 1080×1920`, `Apresentação 16:9`.
- Ações: **Gerar**, **Salvar preset**, **Exportar**.

2) **Coluna esquerda (Outline + Templates)**
- Aba **Estrutura**: lista de slides/cards e ordem.
- Aba **Templates**: escolher layout inicial (ex.: “Before/After”, “Checklist”, “3 pilares”, “Timeline”).
- Aba **Assets**: imagens/ícones (biblioteca + uploads).

3) **Centro (Preview/Canvas)**
- Mostra o frame na proporção real.
- Badge fixo: `1080×1080 · 1.17MP` (ou equivalente) + safe area overlay.
- Antes de gerar: o preview é “wireframe” (não precisa render final), mas já mostra a dimensão para orientar a Gabi.

4) **Coluna direita (Config + Brief/Pprompt)**

**(A) Brief (prompt guiado)**
- Campo “Objetivo” (1 linha)
- Campo “Tema”
- Campo “Público”
- Campo “Tom” (dropdown)
- Campo “CTA”
- Campo “Restrições”

**(B) Configs realistas (por tipo)**
- Apresentação:
  - `Slides: 5 / 6 / 7 / 8` (presets)
  - `Densidade: breve / média / detalhada` (padrão Gamma)[^6]
  - `Layout base`: dropdown de layouts (padrão Pitch/Beautiful.ai)[^3][^4]
  - `Brand kit`: usar config da marca + toggle “forçar logo”

- Imagem:
  - `Tamanho`: presets (1080×1080, 1080×1350, 1080×1920)
  - `Estilo visual`: dropdown (foto/ilustração/3D/flat)
  - `Segurança`: “evitar texto pequeno”, “evitar faces”, etc.

**O que NÃO colocar (porque vira ‘opção irreal’)**
- Inputs numéricos livres para dimensões, grid/colunas, tamanho de fonte, espaçamentos: devem ser consequência de **preset + template** (e/ou ajustes no editor posterior), não de um painel de “números mágicos”.
- Controles que permitam valores fora de faixas comuns (ex.: 999 slides, 20.000×20.000px, margens negativas).

---

## Recomendações práticas para o produto

1) Reduzir o painel de configs para ~6–10 controles no máximo por tipo.
2) Aumentar poder via **templates de layout** e não via “valores livres”.
3) Preview sempre mostrar dimensão e safe area antes de gerar.

---

## Fontes

[^1]: Canva editor layout (sidebar + canvas + toolbar) descrito em guia de interface do Canva: https://www.buzzcube.io/blog/how-use-canva-beginners-guide
[^2]: Brand kit/Styles no editor do Canva: https://mainframe.pixelhaze.academy/course/canva-for-presentations-5-1-branding-your-presentation/
[^3]: Beautiful.ai “Smart Slides” auto-ajustam layout/spacing: https://www.beautiful.ai/presentation-software
[^4]: Pitch templates + slide layouts (timeline, grids etc.): https://pitch.com/use-cases/presentation-maker
[^5]: Pitch “Style builder / slide style”: https://help.pitch.com/en/articles/4059534-create-your-own-slide-style
[^6]: Gamma (configurar número de cards/temas antes de gerar; outline): https://lilys.ai/en/notes/gamma-ai-20251203/gamma-build-stunning-presentations
[^7]: Slidebean (IA para arranjo/layout): https://www.toolsforhumans.ai/ai-tools/slidebean
[^8]: Microsoft PowerPoint (Copilot para outline/layout/brand assets): https://powerpoint.cloud.microsoft/create/en/pitch-deck/
