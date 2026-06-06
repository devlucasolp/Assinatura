'use client'

import { useState, useTransition } from 'react'
import { Pencil, RotateCcw, Check, X } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { useToast } from '@/contexts/ToastContext'
import { updateSkill, resetSkill, type SkillCatalogItem } from './actions'

const CATEGORY_LABEL: Record<SkillCatalogItem['category'], string> = {
  core:  'Núcleo',
  asana: 'Asana',
  media: 'Mídia',
}

const CATEGORY_BADGE: Record<SkillCatalogItem['category'], string> = {
  core:  'bg-violet-50 text-violet-700 dark:bg-violet-950/40 dark:text-violet-400',
  asana: 'bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400',
  media: 'bg-sky-50 text-sky-700 dark:bg-sky-950/40 dark:text-sky-400',
}

export function SkillsCatalogClient({ initial }: { initial: SkillCatalogItem[] }) {
  const { toast }            = useToast()
  const [skills, setSkills]  = useState(initial)
  const [editing, setEditing] = useState<string | null>(null)
  const [draft, setDraft]    = useState<{ name: string; description: string }>({ name: '', description: '' })
  const [pending, startTx]   = useTransition()

  const startEdit = (s: SkillCatalogItem) => {
    setEditing(s.id)
    setDraft({ name: s.name, description: s.description })
  }

  const cancelEdit = () => setEditing(null)

  const save = (s: SkillCatalogItem) => {
    startTx(async () => {
      const patch: { name?: string; description?: string } = {}
      if (draft.name !== s.name)               patch.name = draft.name
      if (draft.description !== s.description) patch.description = draft.description

      if (Object.keys(patch).length === 0) {
        cancelEdit(); return
      }

      const res = await updateSkill(s.id, patch)
      if (res.error) {
        toast(res.error, 'error')
      } else if (res.skill) {
        setSkills(prev => prev.map(x => x.id === s.id ? res.skill! : x))
        toast('Skill atualizada.', 'success')
        cancelEdit()
      }
    })
  }

  const reset = (s: SkillCatalogItem) => {
    if (!confirm(`Restaurar nome e descrição padrão de "${s.default_name}"?`)) return
    startTx(async () => {
      const res = await resetSkill(s.id)
      if (res.error) {
        toast(res.error, 'error')
      } else if (res.skill) {
        setSkills(prev => prev.map(x => x.id === s.id ? res.skill! : x))
        toast('Padrão restaurado.', 'success')
      }
    })
  }

  const grouped = skills.reduce<Record<SkillCatalogItem['category'], SkillCatalogItem[]>>(
    (acc, s) => { (acc[s.category] ??= []).push(s); return acc },
    { core: [], asana: [], media: [] },
  )

  return (
    <div className="flex flex-col gap-6">
      {(Object.keys(grouped) as SkillCatalogItem['category'][]).map(cat => (
        grouped[cat].length > 0 && (
          <section key={cat}>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-2 px-1">
              {CATEGORY_LABEL[cat]}
            </h3>
            <div className="flex flex-col gap-2">
              {grouped[cat].map(s => {
                const isEditing = editing === s.id
                return (
                  <div
                    key={s.id}
                    className="p-4 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800"
                  >
                    {isEditing ? (
                      <div className="flex flex-col gap-3">
                        <Input
                          value={draft.name}
                          onChange={e => setDraft(d => ({ ...d, name: e.target.value }))}
                          placeholder={s.default_name}
                        />
                        <Textarea
                          rows={2}
                          value={draft.description}
                          onChange={e => setDraft(d => ({ ...d, description: e.target.value }))}
                          placeholder={s.default_description}
                        />
                        <div className="flex items-center justify-between gap-2">
                          <p className="text-[10px] font-mono text-zinc-400">id: {s.id}</p>
                          <div className="flex gap-2">
                            <button
                              onClick={cancelEdit}
                              disabled={pending}
                              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs rounded-md border border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
                            >
                              <X className="w-3 h-3" />
                              Cancelar
                            </button>
                            <button
                              onClick={() => save(s)}
                              disabled={pending}
                              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs rounded-md bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50 transition-colors"
                            >
                              <Check className="w-3 h-3" />
                              Salvar
                            </button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="text-sm font-semibold text-zinc-900 dark:text-white">{s.name}</p>
                            <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${CATEGORY_BADGE[s.category]}`}>
                              {CATEGORY_LABEL[s.category]}
                            </span>
                            {s.always_on && (
                              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400">
                                Sempre ativa
                              </span>
                            )}
                            {s.customized && (
                              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400">
                                Customizado
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 leading-relaxed">{s.description}</p>
                          <p className="text-[10px] font-mono text-zinc-400 dark:text-zinc-500 mt-1.5">intent: {s.id}</p>
                        </div>
                        <div className="flex gap-1 shrink-0">
                          {s.customized && (
                            <button
                              onClick={() => reset(s)}
                              disabled={pending}
                              title="Restaurar padrão"
                              className="p-1.5 rounded-md text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                            >
                              <RotateCcw className="w-3.5 h-3.5" />
                            </button>
                          )}
                          <button
                            onClick={() => startEdit(s)}
                            disabled={pending}
                            title="Editar"
                            className="p-1.5 rounded-md text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                          >
                            <Pencil className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </section>
        )
      ))}
    </div>
  )
}
