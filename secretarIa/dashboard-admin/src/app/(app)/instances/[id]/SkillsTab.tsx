'use client'

import { useEffect, useState, useTransition } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { Toggle } from '@/components/ui/Toggle'
import { fetchInstanceSkills, updateInstanceSkills, type InstanceSkill } from './skills-actions'

const CATEGORY_LABEL: Record<InstanceSkill['category'], string> = {
  core:  'Núcleo',
  asana: 'Asana',
  media: 'Mídia',
}

const CATEGORY_BADGE: Record<InstanceSkill['category'], string> = {
  core:  'bg-violet-50 text-violet-700 dark:bg-violet-950/40 dark:text-violet-400',
  asana: 'bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400',
  media: 'bg-sky-50 text-sky-700 dark:bg-sky-950/40 dark:text-sky-400',
}

export function SkillsTab({ instanceId }: { instanceId: string }) {
  const { toast }              = useToast()
  const [skills, setSkills]    = useState<InstanceSkill[]>([])
  const [dirty, setDirty]      = useState<Record<string, boolean>>({})
  const [loading, setLoading]  = useState(true)
  const [saving, startSaving]  = useTransition()

  useEffect(() => {
    fetchInstanceSkills(instanceId).then(s => {
      setSkills(s)
      setLoading(false)
    })
  }, [instanceId])

  const handleToggle = (id: string, next: boolean) => {
    setDirty(prev => ({ ...prev, [id]: next }))
    setSkills(prev => prev.map(s => s.id === id ? { ...s, enabled: next } : s))
  }

  const handleSave = () => {
    if (Object.keys(dirty).length === 0) return
    startSaving(async () => {
      const res = await updateInstanceSkills(instanceId, dirty)
      if (res.error) {
        toast(res.error, 'error')
      } else {
        toast(`${Object.keys(dirty).length} skill(s) atualizada(s).`, 'success')
        setDirty({})
      }
    })
  }

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-16 bg-zinc-100 dark:bg-zinc-800 rounded-xl animate-pulse" />
        ))}
      </div>
    )
  }

  const grouped = skills.reduce<Record<InstanceSkill['category'], InstanceSkill[]>>(
    (acc, s) => { (acc[s.category] ??= []).push(s); return acc },
    { core: [], asana: [], media: [] },
  )

  const dirtyCount = Object.keys(dirty).length

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Liga ou desliga cada habilidade só para esta instância. Skills marcadas como{' '}
          <span className="font-semibold">Sempre ativa</span> não podem ser desligadas.
        </p>
        {dirtyCount > 0 && (
          <button
            onClick={handleSave}
            disabled={saving}
            className="text-xs font-medium px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50 transition-colors"
          >
            {saving ? 'Salvando…' : `Salvar ${dirtyCount} alteração${dirtyCount > 1 ? 'ões' : ''}`}
          </button>
        )}
      </div>

      {(Object.keys(grouped) as InstanceSkill['category'][]).map(cat => (
        grouped[cat].length > 0 && (
          <section key={cat}>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-2 px-1">
              {CATEGORY_LABEL[cat]}
            </h3>
            <div className="flex flex-col gap-1.5">
              {grouped[cat].map(skill => (
                <div
                  key={skill.id}
                  className="flex items-center justify-between gap-4 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="text-sm font-semibold text-zinc-900 dark:text-white">{skill.name}</p>
                      <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${CATEGORY_BADGE[skill.category]}`}>
                        {CATEGORY_LABEL[skill.category]}
                      </span>
                      {skill.always_on && (
                        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400">
                          Sempre ativa
                        </span>
                      )}
                      {dirty[skill.id] !== undefined && (
                        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400">
                          Não salvo
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">{skill.description}</p>
                  </div>
                  <Toggle
                    checked={skill.enabled}
                    onChange={(next) => handleToggle(skill.id, next)}
                    disabled={skill.always_on}
                    ariaLabel={`Ativar ${skill.name}`}
                  />
                </div>
              ))}
            </div>
          </section>
        )
      ))}
    </div>
  )
}
