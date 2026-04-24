---
description: Ingere um documento bruto na knowledge-base (cria página + atualiza index/log/canvas)
argument-hint: <caminho/ao/arquivo>
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# /memory-ingest

Você é o **mantenedor da knowledge-base** deste vault. O schema vive em `knowledge-base/CLAUDE.md` — leia-o PRIMEIRO se ainda não leu nesta sessão.

## Entrada

Arquivo a ingerir: `$ARGUMENTS`

Se `$ARGUMENTS` estiver vazio, pergunte ao usuário qual arquivo ingerir.

## Procedimento (execute em ordem)

1. **Ler o schema** — `knowledge-base/CLAUDE.md` (se ainda não foi lido nesta sessão).
2. **Ler o arquivo-fonte** — `$ARGUMENTS` completo. Se for diretório, liste `.md` dentro e pergunte qual.
3. **Classificar** — determine o `type` com base no conteúdo:
   - contém "decidimos / em vez de / trade-off" → `decision`
   - descreve feature pronta → `feature`
   - fala de API/SDK externo → `integration`
   - cert/OAuth/auth/key → `security`
   - fluxo ponta-a-ponta → `workflow`
   - diagrama/padrão/C4 → `architecture`
4. **Extrair** os blocos exigidos pelo template:
   - **Resumo** (2–4 frases, suas palavras — não copiar prosa do fonte).
   - **Detalhes** estruturados (headings + listas).
   - **Decisões Tomadas** (trade-offs explícitos).
   - **Learnings** (bugs, pegadinhas, dívidas).
   - **Relacionados** (use `Grep` no `wiki/` para achar páginas com tags ou termos em comum).
5. **Escolher o slug** — kebab-case, curto, descritivo. Ex: `multi-empresa`, `serpro-timeout`.
6. **Escrever a página** em `knowledge-base/wiki/<pasta-do-type>/<slug>.md` com o frontmatter obrigatório:

   ```yaml
   ---
   title: ...
   type: <type>
   tags: [...]
   sources: [<caminho/ao/arquivo>]
   created: <hoje ISO>
   updated: <hoje ISO>
   ---
   ```

7. **Atualizar `index.md`** — adicionar linha `- [Título](pasta/slug.md) — resumo em 1 frase` na seção do type (remover placeholder "Nenhuma página ainda" se presente).
8. **Append `log.md`** — nova linha:
   `- \`<YYYY-MM-DD HH:MM> | ingest | <slug> | <pasta>/<slug>.md\``
9. **Atualizar `tracking.canvas`** — adicionar nó `type: "file"` com `"file": "knowledge-base/wiki/<pasta>/<slug>.md"` e um edge do último nó textual de data para ele. Use `Read` para pegar o JSON atual, modifique, `Write` de volta.
10. **Relatar** ao usuário: caminho da página, seção atualizada no index, link clicável.

## Regras (inegociáveis)

- Nunca reescrever o `log.md`, apenas append.
- Nunca sobrescrever uma página existente sem confirmar com o usuário primeiro — se o slug já existe, proponha `<slug>-v2` ou sugerir merge.
- Links dentro da wiki são sempre **relativos**.
- Se detectar contradição com página existente, adicionar `> ⚠️ CONFLITO: ver [outra-pagina.md](...)` na página antiga e relatar ao usuário.

## Saída esperada

```
✅ Ingerido: feature-multi-empresa.md → knowledge-base/wiki/features/multi-empresa.md
📚 Index atualizado (seção Features)
📜 Log: 2026-04-22 14:32
🎨 Canvas: nó adicionado e conectado

Próximo passo sugerido: /memory-query "…"
```
