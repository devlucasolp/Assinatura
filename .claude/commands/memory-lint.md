---
description: Auditoria de saúde da wiki (links quebrados, páginas órfãs, contradições, claims desatualizados)
allowed-tools: Read, Edit, Bash, Grep, Glob
---

# /memory-lint

Você é o **auditor da knowledge-base**. Varre `knowledge-base/wiki/` atrás de inconsistências e produz relatório acionável. **Não escreve páginas novas** — apenas relata e (se autorizado) atualiza `overview.md` seção `auto:debt`.

## Procedimento

1. **Ler schema** — `knowledge-base/CLAUDE.md`.
2. **Enumerar páginas** — `Glob` em `knowledge-base/wiki/**/*.md`.
3. **Checar frontmatter** — cada página deve ter `title`, `type`, `created`, `updated`. Liste as que faltam.
4. **Checar links** — para cada link relativo `[...](path.md)` em cada página, verificar que o arquivo existe com `Bash test -f`.
5. **Detectar órfãs** — páginas que nenhuma outra página linka E que não estão em `index.md`.
6. **Detectar conceitos sem página** — termos que aparecem em 3+ páginas mas não têm página própria (`Grep` heurístico: substantivos capitalizados recorrentes).
7. **Contradições** — páginas com tags iguais mas afirmações conflitantes. Heurística: procurar por padrão `> ⚠️ CONFLITO` já marcado; depois usar diff semântico leve em páginas da mesma pasta.
8. **Claims desatualizados** — páginas com `updated` > 60 dias onde o código (quando acessível via `git log`) foi tocado depois.
9. **Gerar relatório** em prosa estruturada:

   ```
   🩺 LINT REPORT — 2026-04-22

   ❌ Frontmatter faltando (2)
     - features/multi-empresa.md → falta `updated`
     - security/cert.md → falta `tags`

   ❌ Links quebrados (1)
     - architecture/frontend.md → [auth-flow](security/auth.md) ❌ (arquivo não existe)

   🧟 Páginas órfãs (1)
     - outputs/2026-03-15-serpro.md (não citada em index nem em outras)

   🧩 Conceitos sem página (2)
     - "procuração" (mencionado em 4 páginas)
     - "certificado A1" (mencionado em 6 páginas)

   ⚠️ Possíveis contradições (1)
     - decisions/adr-0003.md vs features/batch-job.md

   🕰️ Claims desatualizados (1)
     - integrations/calima.md (updated 2026-01-10, código tocado 2026-04-12)
   ```

10. **Perguntar** se deseja que o relatório seja gravado em `overview.md` na seção `<!-- auto:debt -->`. Se sim, edite apenas essa seção com `Edit`.
11. **Append** uma linha em `log.md`: `| lint | <N issues encontradas> | overview.md#debt` (apenas se o relatório foi gravado).

## Regras

- **Nunca apagar** páginas órfãs automaticamente — só relatar.
- **Nunca** consertar links quebrados sem confirmação (o link pode estar certo e o arquivo é que sumiu indevidamente).
- Relatório é sempre idempotente — rodar duas vezes no mesmo estado produz saída equivalente.
