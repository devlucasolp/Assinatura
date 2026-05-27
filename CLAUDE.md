# Assinatura â€” CLAUDE.md

> **Projeto:** Assinatura Marca PrÃ³pria (cliente: Amanda, Gabi, Marcelle)
> **Maintainer:** Claude Code + Cowork
> **VersÃ£o do schema:** Tzolkin Karpathy v2.0
> **KB canÃ´nica:** `knowledge-base/` (este folder) â€” substitui `designer/knowledge-base/` da v1

---

## âš ï¸ Estado da migraÃ§Ã£o (2026-05-14)

A KB foi promovida de `designer/knowledge-base/` para `knowledge-base/` no nÃ­vel do projeto Assinatura, para refletir que cobre os **3 sub-produtos** (Secretaria AI, Designer, Marcelle) e nÃ£o apenas o Designer.

- âœ… Nova KB criada em `knowledge-base/` com schema v2.0 (namespaces, paleta canvas, /commit)
- â³ ConteÃºdo da wiki antiga ainda em `designer/knowledge-base/wiki/`
- ðŸ“‹ Para finalizar: rodar `knowledge-base/MIGRATE-KB-CONTENT.ps1`

AtÃ© o script ser rodado, **a KB ativa em produÃ§Ã£o continua sendo `designer/knowledge-base/`**. Comandos `/memory-*` ainda operam ali.

---

## Produtos em desenvolvimento

| Produto | ResponsÃ¡vel | Namespace na KB | Status | Deadline MVP atual |
|---|---|---|---|---|
| Secretaria A.I. (Gabi) | Lucas | `wiki/*/secretaria/` | â±ï¸ MÃªs 2 (Sem 5â€“8) | 19/05/2026 |
| AutomaÃ§Ã£o NotificaÃ§Ã£o (Marcelle) | Lucas + Saleco | `wiki/*/marcelle/` | â±ï¸ MÃªs 2 | 16/06/2026 |
| Designer IA | Saleco | `wiki/*/designer/` | ðŸ”„ Sprint 1 | â€” |

## Estrutura do repositÃ³rio

```
Assinatura/
â”œâ”€â”€ CLAUDE.md              â† este arquivo
â”œâ”€â”€ CONTEXTO.md            â† roadmap de produto (leitura rÃ¡pida)
â”œâ”€â”€ knowledge-base/        â† KB canÃ´nica v2.0 (Karpathy Tzolkin)
â”‚   â”œâ”€â”€ CLAUDE.md          â† schema + regras
â”‚   â”œâ”€â”€ MIGRATE-KB-CONTENT.ps1  â† script de migraÃ§Ã£o (rodar 1x)
â”‚   â”œâ”€â”€ git/config.json    â† target do /memory-consolidate
â”‚   â””â”€â”€ wiki/              â† (vazia atÃ© MIGRATE rodar)
â”‚       â”œâ”€â”€ architecture/{secretaria,designer,marcelle}/
â”‚       â”œâ”€â”€ features/{secretaria,designer,marcelle}/
â”‚       â”œâ”€â”€ workflows/{secretaria,designer,marcelle}/
â”‚       â”œâ”€â”€ outputs/{designer}/                   (+ plano)
â”‚       â”œâ”€â”€ integrations/                         (cross-cutting)
â”‚       â”œâ”€â”€ decisions/                            (cross-cutting)
â”‚       â”œâ”€â”€ stakeholders/                         (cross-cutting)
â”‚       â”œâ”€â”€ security/                             (cross-cutting)
â”‚       â””â”€â”€ migrations/                           (gerado)
â”œâ”€â”€ designer/knowledge-base/  â† KB v1 ATIVA (serÃ¡ movida para .legacy apÃ³s migrate)
â”œâ”€â”€ Bot_Gabi/Assinatura/   â† cÃ³digo Secretaria AI (Python/FastAPI)
â”œâ”€â”€ designer/
â”‚   â”œâ”€â”€ frontend/          â† Next.js App Router
â”‚   â””â”€â”€ backend/           â† Express + Prisma + PostgreSQL
â””â”€â”€ .claude/
    â”œâ”€â”€ commands/          â† /memory-ingest, /memory-query, /memory-lint, /memory-consolidate, /commit
    â””â”€â”€ skills/memory/     â† SKILL.md (Cowork)
```

## Protocolo de sessÃ£o

1. LÃª este arquivo
2. LÃª `knowledge-base/CLAUDE.md` (schema v2.0)
3. LÃª `knowledge-base/wiki/index.md` se jÃ¡ houver conteÃºdo migrado; senÃ£o `designer/knowledge-base/wiki/index.md`
4. LÃª Ãºltimas 5 entradas do `log.md` ativo
5. Confirma estado atual em 1 frase

## Comandos disponÃ­veis

| Comando | Quando usar |
|---|---|
| `/memory-ingest <arquivo>` | Novo doc, feature, ADR, meeting note |
| `/memory-query <pergunta>` | Consulta tÃ©cnica sobre o projeto |
| `/memory-lint` | Auditoria de saÃºde da KB |
| `/memory-consolidate` | Fechamento semanal (git log â†” wiki) |
| `/commit [tipo: msg]` | Ingest + commit + push num passo (v2.0) |

## Regras inviolÃ¡veis

- `raw/` Ã© read-only
- KB canÃ´nica Ã© `knowledge-base/wiki/` (apÃ³s migrate); `designer/knowledge-base/wiki/` Ã© legado em transiÃ§Ã£o
- PÃ¡ginas mono-produto vÃ£o para namespace (`wiki/features/secretaria/x.md`)
- PÃ¡ginas cross-cutting ficam planas (`wiki/decisions/adr-003.md`)
- Todo ingest atualiza `index.md` + `log.md` + `tracking.canvas`
- HipÃ³teses nÃ£o-validadas marcadas com `ðŸŸ¡ HIPÃ“TESE`

## ReferÃªncia

- Template Tzolkin Karpathy v2.0: `D:/CÃ³digos/Tzolkin/.tzolkin/karpathy/`
- CLAUDE.md raiz da Tzolkin: `D:/CÃ³digos/Tzolkin/CLAUDE.md`

