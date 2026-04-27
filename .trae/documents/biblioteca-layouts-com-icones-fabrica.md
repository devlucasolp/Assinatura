# Biblioteca de layouts com ícones — Fábrica

## Objetivo
Padronizar uma biblioteca de layouts (seleção “template-first”) com **ícones + nomes canônicos** para reduzir ambiguidade entre modelos (LLMs/geradores) e manter consistência visual.

## Regras gerais
- **Nome canônico (layoutKey)**: curto, estável e “prompt-friendly” (ex.: `texto-esq/imagem-dir`).
- **Ícone**: pictograma minimalista que represente a estrutura (não a estética).
- **Compatibilidade**: todo layout deve funcionar em **16:9**, **4:3** e **A4** (regras internas adaptam margens/safe-area).
- **Safe-area**: sempre considerar margens internas (recomendado 5–8% do frame) para texto e elementos críticos.

## Conjunto inicial (MVP)
> Sugestão: exibir como grid 3–4 colunas (desktop), cada item com ícone + nome.

| layoutKey | Nome exibido | Ícone (wireframe) | Uso típico | Prompt hint (para modelos) |
|---|---|---|---|---|
| `texto-esq/imagem-dir` | Texto à esquerda / Imagem à direita | `[TXT][ IMG ]` | Explicação + evidência visual | “Coluna esquerda: título + bullets; coluna direita: imagem principal com legenda curta.” |
| `imagem-esq/texto-dir` | Imagem à esquerda / Texto à direita | `[IMG ][ TXT]` | Produto + mensagem | “Imagem grande à esquerda; à direita: heading + 3 bullets.” |
| `imagem-topo/texto-base` | Imagem em cima / Texto embaixo | `[ IMG ]\n[ TXT ]` | Capa/hero + contexto | “Imagem ocupando topo; abaixo: título + parágrafo curto.” |
| `titulo/bullets` | Título + bullets | `[TITLE]\n[• • •]` | Slide de lista | “Título curto; 3–5 bullets; evitar texto longo.” |
| `2-colunas-texto` | Duas colunas de texto | `[TXT][TXT]` | Comparação/argumento | “Duas colunas equilibradas; cada uma com subtítulo + 2–3 bullets.” |
| `antes/depois` | Antes / Depois | `[BEFORE][AFTER]` | Transformação | “Duas metades; rótulos ‘Antes’ e ‘Depois’; manter simetria.” |

## Metadados recomendados por layout
Cada layout pode carregar metadados para guiar a geração e o editor:
- `minTextDensity`: `breve | media | detalhada` (limites sugeridos)
- `supportsImages`: boolean
- `slots`: lista de áreas (“title”, “body”, “image”, “caption”, etc.)
- `fallbackLayoutKey`: usado quando o modelo não consegue respeitar a estrutura

## Integração com fontes (envio à IA)
- Ao gerar, inclua:
  - `headingFontAssetId` e `bodyFontAssetId` (ou URLs de download temporárias do Storage).
  - `fallbackFamily` para quando o provedor/modelo não suportar a fonte.
- Se ocorrer fallback, retornar `warnings: FONT_NOT_SUPPORTED` e manter o layout.

## Formatos (presets) suportados
- Apresentação: `presentation_16_9`, `presentation_4_3`
- Documento: `a4_portrait`, `a4_landscape`

## Critérios de “benchmarking de modelos” (para evoluir a biblioteca)
Use uma matriz de testes para comparar modelos/provedores sem depender de opinião:
1) **Fidelidade ao layout**: respeita slots/colunas? (0–2)
2) **Tipografia**: aplica fonte ou falha com fallback previsível? (0–2)
3) **Overflow**: evita texto estourando safe-area? (0–2)
4) **Consistência**: resultado estável em 3 execuções iguais? (0–2)
5) **Tempo/custo**: latência e custo por geração (registrar)

Saída esperada do benchmark: `layoutKey` x `modelo` com scores e principais falhas (ex.: “troca colunas”, “ignora fonte”, “texto fora da safe-area”).
