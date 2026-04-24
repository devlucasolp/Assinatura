---
name: memory
description: Memory management skill no padrão Karpathy LLM-Wiki + Obsidian. Use para ingerir documentos, consultar, auditar ou consolidar a knowledge-base do vault (pasta `knowledge-base/`). Triggers — qualquer pedido do usuário envolvendo "memory-ingest", "memory-query", "memory-lint", "memory-consolidate", "wiki", "knowledge base", "atualizar docs do projeto", "consolidar semana", "registrar decisão (ADR)", ou quando o usuário pedir para lembrar/documentar algo persistentemente entre sessões. Use também quando for instruído a operar sobre arquivos dentro de `knowledge-base/wiki/`.
---

# Memory — Karpathy LLM-Wiki + Obsidian

Esta skill te torna o **mantenedor vivo** de uma knowledge-base em padrão LLM-Wiki, persistida como Obsidian vault dentro da pasta `knowledge-base/` deste workspace.

## Contrato

O arquivo **`knowledge-base/CLAUDE.md`** é o contrato autoritativo: schema de pastas, tipos de página, frontmatter obrigatório, regras invioláveis. **Sempre leia-o antes de operar** (uma vez por sessão é suficiente).

## Quatro operações

Quando o usuário pedir qualquer uma delas, siga o procedimento detalhado no comando equivalente em `.claude/commands/memory-*.md` (são os mesmos procedimentos, documentados lá). Aqui está o resumo:

### 1. Ingest — "adicionar isto na wiki"

Input: caminho de um arquivo (ou conteúdo direto).

1. Ler `knowledge-base/CLAUDE.md` se ainda não leu.
2. Ler o fonte.
3. Classificar o `type` (architecture / feature / decision / integration / security / workflow).
4. Extrair Resumo, Detalhes, Decisões, Learnings, Relacionados (com links relativos existentes descobertos via Grep).
5. Escrever página em `knowledge-base/wiki/<pasta>/<slug>.md` com frontmatter YAML obrigatório.
6. Atualizar `index.md`, append em `log.md`, adicionar nó + edge em `tracking.canvas`.

### 2. Query — "o que a wiki sabe sobre X?"

1. Ler `wiki/index.md` para localizar páginas plausíveis.
2. Ler essas páginas (2–5), opcionalmente `Grep` para termos-chave.
3. Sintetizar resposta em prosa com citações por link relativo.
4. Se nada encontrado, dizer **"wiki não cobre isso ainda"** e sugerir ingest.
5. Oferecer arquivar em `outputs/<hoje>-<slug>.md`.

### 3. Lint — "a wiki está saudável?"

Auditoria somente-leitura (exceto pela seção `auto:debt` de `overview.md`):
- frontmatter faltando
- links quebrados
- páginas órfãs (não citadas em lugar nenhum)
- conceitos recorrentes sem página própria
- contradições explícitas (`> ⚠️ CONFLITO`) ou semânticas
- claims com `updated` > 60 dias sobre código que foi tocado depois

Relatório em prosa. Não apaga nada. Pergunta antes de gravar em `overview.md`.

### 4. Consolidate — "fecha a semana"

1. Checar/criar `knowledge-base/git/config.json` (remote + branch + path do repo).
2. Janela temporal = desde último `migrations/*.md` até hoje.
3. `git log` na janela + eventos de `wiki/log.md` na janela.
4. Correlacionar commit ↔ página. Marcar ✅ sync / ⚠️ gap / ⚠️ doc-sem-código / conflitos.
5. Escrever `wiki/migrations/<hoje>.md` com timeline + gaps + sugestões.
6. Regerar seções `<!-- auto:* -->` de `overview.md` (preserva resto).
7. Append `log.md`, atualizar `tracking.canvas` e `index.md`.

## Regras invioláveis

- **Links relativos** sempre dentro da wiki.
- **Frontmatter YAML obrigatório** em toda página.
- **`log.md` é append-only** — nunca reescrever linhas passadas.
- **Nunca editar `migrations/`** à mão — é output gerado.
- **Nunca sobrescrever** página existente sem confirmar.
- **Flag contradições** com `> ⚠️ CONFLITO: ...`.
- **Canvas refs** usam `"file": "knowledge-base/wiki/..."` com o prefixo `knowledge-base/` (o vault raiz é o folder acima).
- **Nunca inventar** — se a wiki não cobre, diga.

## Obsidian Canvas (`wiki/tracking.canvas`)

JSON nativo. Dois tipos de nó:
- `"type": "text"` — marcos (datas, epics, decisões).
- `"type": "file"` + `"file": "knowledge-base/wiki/..."` — embeda uma página.

Edges conectam evolução cronológica. Toda nova página adicionada pelo ingest ganha um nó file + edge a partir do nó textual da data corrente.

## Referência cruzada

Para Claude Code, as mesmas 4 operações estão disponíveis como slash commands:

- `/memory-ingest <arquivo>` → `.claude/commands/memory-ingest.md`
- `/memory-query <pergunta>` → `.claude/commands/memory-query.md`
- `/memory-lint` → `.claude/commands/memory-lint.md`
- `/memory-consolidate` → `.claude/commands/memory-consolidate.md`

Se o usuário estiver rodando Claude Code, sugira o comando equivalente em vez de invocar esta skill.

## Quando NÃO usar

- Pedido de edição direta de arquivo fora de `knowledge-base/` (use Edit/Write diretos).
- Resumo one-shot que o usuário não quer persistir (responda no chat, não ingera).
- Pergunta factual geral sem relação com o projeto (não consulte wiki à toa).

## Primeiro passo em qualquer sessão

```
Read knowledge-base/CLAUDE.md   ← contrato
Read knowledge-base/wiki/index.md  ← catálogo
```

Depois disso, proceda conforme a operação pedida.
