# Projeto Assinatura â€” Knowledge Base Schema (Karpathy v2.0)

> **Contrato** que Claude (Code ou Cowork) lÃª ao operar esta wiki.
> PadrÃ£o: **Karpathy LLM-Wiki + Obsidian Vault + GitHub feedback loop** (Tzolkin v2.0).
> Cobre os 3 sub-produtos do contrato Assinatura: **Secretaria A.I. (Gabi)**, **AutomaÃ§Ã£o NotificaÃ§Ã£o (Marcelle)** e **Designer IA**.
> Status: wiki viva Â· log append-only Â· consolidaÃ§Ã£o semanal Â· canvas timeline.

---

## âš ï¸ MigraÃ§Ã£o em andamento (2026-05-14)

Esta KB foi criada para substituir a antiga em `Assinatura/designer/knowledge-base/`, que vivia indevidamente dentro de `designer/` apesar de cobrir todos os 3 sub-produtos.

**Estado atual:**
- â³ KB nova em `Assinatura/knowledge-base/` (este folder) â€” estrutura criada, conteÃºdo pendente de migraÃ§Ã£o
- âš ï¸ KB antiga em `Assinatura/designer/knowledge-base/` â€” ainda ativa, contÃ©m todas as pÃ¡ginas
- ðŸ“‹ Script de migraÃ§Ã£o: `MIGRATE-KB-CONTENT.ps1` neste folder (mover wiki pages com namespaces)

Quando a migraÃ§Ã£o for executada, a KB antiga serÃ¡ marcada como `knowledge-base.legacy/` e este folder passarÃ¡ a ser a fonte de verdade.

---

## ðŸ“ Estrutura

```
knowledge-base/
â”œâ”€â”€ CLAUDE.md              â† este arquivo (schema + regras)
â”œâ”€â”€ MIGRATE-KB-CONTENT.ps1 â† script para mover conteÃºdo da KB antiga (rodar 1x)
â”œâ”€â”€ git/
â”‚   â””â”€â”€ config.json        â† repo remoto para consolidate
â””â”€â”€ wiki/
    â”œâ”€â”€ index.md           â† catÃ¡logo master
    â”œâ”€â”€ log.md             â† append-only timeline
    â”œâ”€â”€ overview.md        â† sÃ­ntese dinÃ¢mica
    â”œâ”€â”€ tracking.canvas    â† timeline visual (estilo haylanderform)
    â”œâ”€â”€ architecture/
    â”‚   â”œâ”€â”€ secretaria/    â† arquitetura Bot Gabi (FastAPI)
    â”‚   â”œâ”€â”€ designer/      â† arquitetura Designer (Next+Express)
    â”‚   â””â”€â”€ marcelle/      â† arquitetura AutomaÃ§Ã£o Marcelle
    â”œâ”€â”€ features/
    â”‚   â”œâ”€â”€ secretaria/    â† features Secretaria AI
    â”‚   â”œâ”€â”€ designer/      â† features Designer
    â”‚   â””â”€â”€ marcelle/      â† features Marcelle
    â”œâ”€â”€ integrations/      â† third-parties (plano â€” geralmente cross-cutting)
    â”œâ”€â”€ security/          â† LGPD, OAuth, keys (plano)
    â”œâ”€â”€ workflows/
    â”‚   â”œâ”€â”€ secretaria/
    â”‚   â”œâ”€â”€ designer/
    â”‚   â””â”€â”€ marcelle/
    â”œâ”€â”€ decisions/         â† ADRs (plano â€” frequente cross-cutting)
    â”œâ”€â”€ stakeholders/      â† pessoas e organizaÃ§Ãµes (plano)
    â”œâ”€â”€ migrations/        â† relatÃ³rios semanais (gerado)
    â””â”€â”€ outputs/           â† queries arquivadas (plano por padrÃ£o; pode ter subpasta por produto se volumoso)
```

### PrincÃ­pio de namespaces

- **Use namespace** quando a pÃ¡gina fala **sÃ³ de um sub-produto**.
- **Sem namespace** quando a pÃ¡gina Ã© **cross-cutting** (stakeholders, ADRs sobre infra compartilhada, integraÃ§Ãµes usadas por mais de um sub-produto, outputs de visÃ£o geral).

---

## ðŸ·ï¸ Tipos de PÃ¡gina

| Type           | Pasta           | Quando criar                                              |
| -------------- | --------------- | --------------------------------------------------------- |
| `architecture` | `architecture/` | C4, padrÃµes, system design                                |
| `feature`      | `features/`     | Feature/produto implementado                              |
| `decision`     | `decisions/`    | ADR â€” por que X em vez de Y                               |
| `integration`  | `integrations/` | ServiÃ§o externo (Asana, Stripe, Gemini, Evolution, etc.)  |
| `security`     | `security/`     | LGPD, certs, OAuth, keys                                  |
| `workflow`     | `workflows/`    | Fluxo ponta-a-ponta                                       |
| `migration`    | `migrations/`   | ConsolidaÃ§Ã£o semanal (gerado)                             |
| `output`       | `outputs/`      | Query arquivada                                           |
| `stakeholder`  | `stakeholders/` | Pessoa ou organizaÃ§Ã£o                                     |

---

## ðŸ“„ Template de PÃ¡gina

```yaml
---
title: TÃ­tulo humano
type: feature | decision | integration | security | workflow | architecture | migration | output | stakeholder
namespace: secretaria | designer | marcelle    # OPCIONAL â€” sÃ³ se aplicÃ¡vel
tags: [tag1, tag2]
sources: [caminho/ao/arquivo-origem.md, commit-sha, url]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft | active | deprecated             # OPCIONAL
---

# TÃ­tulo humano

## Resumo
2â€“4 frases.

## Detalhes
ConteÃºdo estruturado.

## DecisÃµes Tomadas
Trade-offs explÃ­citos.

## Learnings
Bugs, patterns, dÃ­vidas tÃ©cnicas.

## Relacionados
- [Outro](../pasta/outra.md) â€” relaÃ§Ã£o
```

---

## ðŸ“œ Rules (inviolÃ¡veis)

1. âœ… **Links relativos sempre** â€” `[Title](features/designer/x.md)`.
2. âœ… **Frontmatter YAML obrigatÃ³rio**.
3. âœ… **Atualizar `index.md` + `log.md` + `tracking.canvas`** a cada operaÃ§Ã£o.
4. âœ… **Nunca editar `migrations/`** manualmente.
5. âœ… **Flag contradiÃ§Ãµes** com `> âš ï¸ CONFLITO: ...`.
6. âœ… **`log.md` Ã© append-only**.
7. âœ… **Canvas refs** â€” vault root = `knowledge-base/`. File-nodes usam `wiki/.../arquivo.md`.
8. âœ… **Nunca editar `raw/`**.
9. âœ… **Sync com GitHub semanal** via `/memory-consolidate`.
10. âœ… **HipÃ³teses nÃ£o-validadas** com `ðŸŸ¡ HIPÃ“TESE`.
11. âœ… **Migrations nÃ£o entram em `index.md`** â€” sÃ³ canvas e overview.

---

## ðŸ› ï¸ As 5 OperaÃ§Ãµes

(Ver `D:/CÃ³digos/Tzolkin/.tzolkin/karpathy/commands/*.md` para procedimentos completos.)

- **`/memory-ingest <arquivo>`** â€” LÃª fonte, cria pÃ¡gina com namespace, atualiza index+log+canvas.
- **`/memory-query <pergunta>`** â€” LÃª index, sintetiza resposta, oferece arquivar em `outputs/`.
- **`/memory-lint`** â€” Auditoria: links, Ã³rfÃ£s, hipÃ³teses pendentes, frontmatter, namespace consistente.
- **`/memory-consolidate`** â€” Correlaciona `git log` com wiki, gera `migrations/YYYY-MM-DD.md`.
- **`/commit [tipo: msg]`** â€” Ingest + git commit + push + canvas (nÃ³ verde) em 1 passo.

---

## ðŸŽ¨ Canvas (`wiki/tracking.canvas`)

**Layout:** timeline horizontal de save-dates no topo, file-nodes verticais abaixo (estilo `haylanderform`).

**Paleta oficial:**

| Tipo                  | Cor          | CÃ³digo  |
| --------------------- | ------------ | ------- |
| Save-date             | Cinza        | _none_  |
| Commit                | Verde        | `"4"`   |
| DecisÃ£o/Fix           | Laranja      | `"2"`   |
| TODO/Red-flag         | Vermelho     | `"1"`   |
| Ingest                | Roxo         | `"6"`   |
| ConsolidaÃ§Ã£o          | Ciano        | `"5"`   |
| Marco/PrÃ³ximos        | Amarelo      | `"3"`   |
| PÃ¡gina de wiki        | _file node_  | â€”       |

---

## ðŸ”— GitHub Correlation

`knowledge-base/git/config.json` â€” campos `remote`, `branch`, `path`.

Como o projeto Assinatura tem 2 sub-pastas com cÃ³digo (`Bot_Gabi/`, `designer/`), o `path` aponta para a raiz: o `/memory-consolidate` percorre commits em ambos.

```json
{
  "remote": "https://github.com/<user>/<repo>",
  "branch": "main",
  "path": ".."
}
```

(`..` porque a KB estÃ¡ em `Assinatura/knowledge-base/` e o git estÃ¡ em `Assinatura/` ou raiz do projeto. Ajustar conforme o setup real do git.)

---

**VersÃ£o:** 2.0
**Data:** 2026-05-14
**Mantenedor:** Tzolkin (Gustavo + Lucas) + Claude (Code + Cowork)
**ReferÃªncia:** `D:/CÃ³digos/Tzolkin/.tzolkin/karpathy/`

