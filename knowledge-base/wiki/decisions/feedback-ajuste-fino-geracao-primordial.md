# Feedback e Estratégia de Ajuste Fino — Geração Primordial do Assinatura

## Contexto
Data: 2026-05-24  
Projeto: Assinatura (Design Studio)  
Última evolução: persistência de anexos, histórico de conversa na galeria e revisor mais holístico

---

## Feedback do Usuário (Pontos Positivos)

✅ **Layout:** Geração de layout ficou "show"  
✅ **Imagens (Nano Banana):** Imagens são geradas corretamente e se encaixam no design  
✅ **Texto não cortado:** Textos não estão sendo mais cortados pela própria layer (avanço!)

---

## Problemas Identificados e Observações

1. **Textos sempre se sobrepõem de alguma forma**
   - Título sobre conteúdo
   - Todo mundo em cima da imagem e do fundo
   - Sem distinção clara
   - Sem efeito de troca/separação visual

2. **“Templates de escrita” vs. Hierarquia Visual**
   - A dúvida: “seria o melhor a se fazer no caso de uma LLM?”
   - O que falta: IA entender **padrões de tipografia e hierarquia visual** além do copy

3. **Exemplo visual**
   - Slide “Nossa Identidade Visual”
   - Título + conteúdo em cima de imagem, sem respiro, sem contraste ou overlay que ajude

---

## Boas Práticas Pesquisadas (Textos sobre Imagem e Hierarquia)

### A. Legibilidade e Contraste (Obrigatórios)
1. **Semi-transparente atrás do texto**
   - Retângulo ou forma arredondada
   - Preto/marinho/escuro com 20–30% de opacidade
   - Não bloqueie elementos chave (rostos, logos, pontos focais)

2. **Overlay total ou gradiente**
   - Para imagens muito ocupadas (paisagens, cenas de festa, contrastes altos)
   - Gradiente que fica mais opaco onde o texto está

3. **Contraste alto**
   - Branco em fundo escuro ou vice-versa
   - *Sempre* quando há foto, imagem ou fundo complexo: defina `contrastBackground=true`

### B. Hierarquia Visual
1. **Limitar fontes:** Máximo 2 fontes por design
2. **Distinção clara entre roles:**
   - Eyebrow/tag: pequena, caps, alto contraste
   - Título: grande, negrito, peso 800–bold
   - Subtítulo/lead: médio, peso normal/600
   - Corpo: pequeno, peso normal, lineHeight 1.45–1.6
3. **Gap mínimo entre layers:** `max(20px, fontSize_anterior × 0.5)`
4. **Nunca sobrepor:** `y_proximo ≥ y_anterior + height_anterior + gap_mínimo`

### C. Posicionamento e Composição
1. **Alinhe com a composição da foto**
   - Use espaços vazios naturais (céus, paredes claras, áreas de respiro)
2. **Regra dos terços**
   - Posicione texto em um terço da moldura para equilíbrio natural
3. **Efeitos sutis de separação**
   - Sombra leve no texto (usar com moderação)
   - Linhas separadoras
   - Elementos decorativos leves

---

## Estado Atual da Implementação

### O que já está bom
- Templates definidos em `lib/templates/presentation.ts` (10 templates, incluindo `full-bleed`)
- Tipos por role (`FONT_SIZE` e `FONT_WEIGHT` em `agents/design/index.ts`)
- Contraste finalizado via `finalizeSlideContrast`
- Limite de layers (max 7) no Nano Banana
- Zonas pixel-precisas passadas para Nano Banana quando disponíveis

### O que ainda pode ser melhorado
1. **Full-bleed template (imagem full-screen + texto):**
   - Hoje: texto direto na imagem sem overlay/gradiente
   - Problema: texto “some” em fundos complexos
   - Solução: garantir `contrastBackground` + overlay/gradiente padrão para esse template

2. **Hierarquia visual e espaçamento:**
   - A instrução existe no `generateTextLayers` (ai.ts:113–200), mas pode ser mais enfatizada
   - Sobreposição de texto/título ainda acontece
   - Vamos garantir que o *“NUNCA sobrepor layers”* seja reforçado

3. **DesignDocument híbrido (novo fluxo):**
   - Já tem roles semânticos (`eyebrow`, `headline`, `subtitle`, `body`, `caption`, `cta`) em `lib/designDocument.ts`
   - Já tem tokens de tipografia (`display`, `heading`, `body`)
   - Comportamentos de texto: `auto-fit-text`, `balance-lines`, `smart-contrast`
   - Faltando: garantir que esses comportamentos sejam realmente aplicados na compilação para layers

---

## Estratégia de Ajuste Fino (3 Passos Prioritários)

### Passo 1 — Fixar Template Full-Bleed (Prioridade Alta)
- Modificar o template `full-bleed` para incluir um *overlay padrão* por design
- Garantir que, por padrão, todo texto nesse template venha com `contrastBackground=true`
- Adicionar um *shape/container* semântico no DesignDocument para esse tipo de layout
- Compilar esse container para um layer de fundo semi-transparente na conversão para `DesignPage[]`

### Passo 2 — Reforçar Hierarquia e Espaçamento (Prioridade Alta)
- Atualizar a instrução do `generateTextLayers` em `ai.ts` para:
  - Diminuir o limite de layers de texto de 4 para 3 (ou até 2, preferindo menos)
  - Enfatizar *“1 estrutura hierárquica clara”* por slide
  - Aumentar o `gap_mínimo` em 20–30% para mais respiro
  - Proibir sobreposição de forma explícita, com exemplo visual de “errado” e “correto”
- Melhorar o `zoneToLayer` em `agents/design/index.ts` para garantir que as zonas não se sobreponham mesmo quando `textLayers` são injetados

### Passo 3 — Melhorar Compreensão da IA sobre Hierarquia Visual (Prioridade Média)
- Não usar “templates de escrita” rígidos; em vez disso:
  - Reforçar as roles semânticas no DesignDocument
  - Adicionar mais `behaviors` específicos para texto sobre imagem
  - Incluir exemplos de “hierarquia boa” vs “hierarquia ruim” no prompt do `generateDesignDocument`
  - Garantir que o `reviewDesignDocument` também valide hierarquia e legibilidade, além de estrutura

---

## Próximos Passos Imediatos

1. **Ajustar o template `full-bleed`**
2. **Reforçar as regras de espaçamento/não sobreposição**
3. **Testar um fluxo completo de geração híbrida com histórico + anexos**
4. **Validar o editor com o novo comportamento**
5. **Documentar o resultado no tracking.canvas**

---

## Arquivos Relevantes para Revisão/Ajuste

| Caminho | Objetivo |
|---------|----------|
| `designer/backend/src/lib/templates/presentation.ts` | Ajustar template `full-bleed` |
| `designer/backend/src/routes/ai.ts` (linha 113) | Reforçar instruções de `generateTextLayers` |
| `designer/backend/src/agents/design/index.ts` | Garantir que zonas não se sobreponham |
| `designer/backend/src/lib/designDocument.ts` | Reforçar roles e behaviors para texto sobre imagem |
| `designer/frontend/src/lib/designContent.ts` | Já atualizado para anexos/sessão no híbrido |

