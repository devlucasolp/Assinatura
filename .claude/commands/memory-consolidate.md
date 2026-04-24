---
description: Consolidação semanal — correlaciona git log com wiki/log.md e gera relatório em migrations/
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# /memory-consolidate

Você é o **historiador da knowledge-base**. Compara a realidade do código (git log) com o que a wiki afirma (`log.md`, páginas) e produz relatório semanal em `knowledge-base/wiki/migrations/YYYY-MM-DD.md`.

## Pré-requisito: remote configurado

Ler `knowledge-base/git/config.json`. Se **não existir**:

1. Perguntar ao usuário: "Qual é o repositório GitHub deste projeto? (url)".
2. Perguntar: "Qual branch? (default: main)".
3. Criar `knowledge-base/git/config.json`:
   ```json
   { "remote": "<url>", "branch": "<branch>", "path": "<subpasta-do-projeto-ou-.>" }
   ```
4. `"path"` é a subpasta do vault onde o `.git` do projeto vive (ex.: `designer` se o git está em `designer/.git`). Se o git está na raiz, use `"."`.

## Procedimento

1. **Ler schema** — `knowledge-base/CLAUDE.md`.
2. **Carregar config** — `knowledge-base/git/config.json`.
3. **Determinar janela temporal** — última consolidação é o mais recente `migrations/*.md`. Se não houver, usa os últimos 7 dias. Se houver, usa `(data_última + 1)` até hoje.
4. **Rodar `git log`** na pasta `<path>` com `--since=<inicio> --until=<fim> --pretty=format:"%h | %ad | %s" --date=short`.
5. **Ler `wiki/log.md`** e extrair eventos na mesma janela.
6. **Correlacionar**:
   - Commit que menciona uma página (por slug ou título) → ✅ sincronizado.
   - Commit sem página correspondente → ⚠️ gap de documentação.
   - Página atualizada sem commit relacionado → ⚠️ doc sem código (ou mudança só de docs — OK, flag leve).
7. **Detectar conflitos** — procurar páginas em `wiki/` cujo `updated` está dentro da janela E cujo conteúdo factual diverge do diff do commit relacionado. (Heurística: palavras-chave de API/rotas/nomes de função.)
8. **Escrever `migrations/<hoje>.md`** com template:

   ```markdown
   ---
   title: Weekly Consolidation — <hoje>
   type: migration
   tags: [migration, consolidation]
   sources: [git log, wiki/log.md]
   created: <hoje>
   updated: <hoje>
   ---

   # Consolidation Report — <hoje>

   **Janela:** <inicio> → <fim>
   **Commits analisados:** N
   **Eventos de wiki:** M

   ## Timeline

   | Data | Evento | Tipo | Status |
   | ---- | ------ | ---- | ------ |
   | …    | …      | impl | ✅      |

   ## Correlação Código ↔ Wiki

   ✅ Sincronizados: N
   ⚠️ Gaps de doc: M
   ⚠️ Doc sem código: K

   ## Gaps Identificados

   - [ ] Documentar <coisa>
   - [ ] ADR sobre <decisão>

   ## Conflitos

   (listar pares commit ↔ página com divergência)

   ## Sugestões

   1. …
   ```

9. **Atualizar `overview.md`** — regenerar as seções `<!-- auto:* -->`:
   - `auto:pillars` ← lista de páginas em `architecture/`.
   - `auto:features` ← todas em `features/`.
   - `auto:integrations` ← todas em `integrations/`.
   - `auto:decisions` ← últimas 5 por `updated` desc.
   - Use `Edit` — preservar o conteúdo livre (fora dos marcadores).
10. **Append `log.md`**:
    `| consolidate | janela X→Y, N commits, M gaps | migrations/<hoje>.md`.
11. **Atualizar `tracking.canvas`**:
    - Adicionar nó textual "📊 Consolidação <hoje>" com cor `"5"` (roxo).
    - Adicionar nó `file` apontando para o relatório gerado.
    - Edge do último nó textual para este.
12. **Atualizar `index.md`** — seção Migrations.
13. **Relatar** ao usuário em prosa: N commits, M gaps, caminho do relatório.

## Regras

- **Nunca** reescrever migrations antigos — são história.
- Se o repo git estiver ausente ou inacessível, abortar com mensagem clara: "Rode este comando no ambiente onde o `.git` está disponível" e NÃO criar relatório vazio.
- Relatório da mesma data sobrescreve apenas com confirmação do usuário.
- Seções livres de `overview.md` (fora dos marcadores `<!-- auto:* -->`) são **preservadas**.

## Execução manual vs agendada

Este comando pode ser disparado manualmente ou por `/schedule` — nada muda no procedimento.
