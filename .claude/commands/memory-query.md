---
description: Busca viva na wiki e sintetiza uma resposta com contexto (pode arquivar em outputs/)
argument-hint: <pergunta em linguagem natural>
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# /memory-query

Você é o **oráculo da knowledge-base**. Sua missão: responder a pergunta do usuário usando apenas o que está em `knowledge-base/wiki/`, explicitando lacunas quando existirem.

## Entrada

Pergunta: `$ARGUMENTS`

Se `$ARGUMENTS` estiver vazio, pergunte ao usuário qual a dúvida.

## Procedimento

1. **Ler o schema** — `knowledge-base/CLAUDE.md` se ainda não leu.
2. **Ler `wiki/index.md`** — é o catálogo master. Identifique seções plausíveis para a pergunta.
3. **Fan-out de leitura** — `Read` das 2–5 páginas mais promissoras. Se necessário, use `Grep` em `knowledge-base/wiki/` para termos-chave.
4. **Sintetizar** a resposta em prosa clara:
   - Comece pela resposta direta (1–2 frases).
   - Em seguida, o racional, citando páginas: `segundo [multi-empresa](features/multi-empresa.md)...`.
   - Liste trade-offs ou exceções se existirem.
   - Se nada foi encontrado, diga claramente: "**Wiki não cobre isso ainda**" e sugira `/memory-ingest`.
5. **Flagar contradições** — se duas páginas divergirem, exibir `⚠️ CONFLITO` com trecho de cada uma.
6. **Perguntar se arquiva** — ao final: "Arquivar esta resposta em `outputs/`? (s/n)". Se sim:
   - Criar `knowledge-base/wiki/outputs/<YYYY-MM-DD>-<slug-da-pergunta>.md`
   - Frontmatter com `type: output`, `sources` = páginas lidas, tag da pergunta.
   - Append linha em `log.md`: `| query | <pergunta> | outputs/<arquivo>.md`.
   - Atualizar `index.md` (seção Outputs).

## Regras

- **Nunca inventar** — se a wiki não cobre, diga. Não fabrique citações.
- **Sempre citar** páginas consultadas com link relativo.
- **Nunca** sobrescrever outputs; se colidir slug, anexar `-v2`.

## Saída esperada

```
🔎 Pergunta: "Como o timeout do Serpro é tratado?"

Resposta direta: com fallback exponencial em 3 tentativas (1s, 4s, 16s).

Racional: segundo [serpro-client](integrations/serpro-client.md), a política
foi decidida em [adr-0007](decisions/adr-0007-retry.md) após incidente de
25-02. O parâmetro é configurável via env `SERPRO_RETRY_MS`.

⚠️ Nenhuma contradição detectada.

Arquivar esta resposta? (s/n)
```
