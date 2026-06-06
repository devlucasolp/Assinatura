'use client'

import { useEffect, useState, useTransition } from 'react'
import { Plus, Trash2, Pencil, X, Check } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Toggle } from '@/components/ui/Toggle'
import { useToast } from '@/contexts/ToastContext'
import {
  fetchCustomSkills,
  createCustomSkill,
  updateCustomSkill,
  deleteCustomSkill,
  type CustomSkill,
  type CustomSkillInput,
} from './custom-skills-actions'

const EMPTY: CustomSkillInput = {
  name: '',
  keywords: [],
  match_whole_word: false,
  response_template: '',
  enabled: true,
}

type Draft = CustomSkillInput & { keywordsRaw: string }

function toDraft(s: CustomSkill | null): Draft {
  if (!s) return { ...EMPTY, keywordsRaw: '' }
  return { ...s, keywordsRaw: s.keywords.join(', ') }
}

function parseKeywords(raw: string): string[] {
  return raw.split(',').map(s => s.trim()).filter(Boolean)
}

export function CustomSkillsSection({ instanceId }: { instanceId: string }) {
  const { toast }              = useToast()
  const [skills, setSkills]    = useState<CustomSkill[]>([])
  const [loading, setLoading]  = useState(true)
  const [editing, setEditing]  = useState<number | 'new' | null>(null)
  const [draft, setDraft]      = useState<Draft>(toDraft(null))
  const [pending, startTx]     = useTransition()

  const reload = async () => {
    const list = await fetchCustomSkills(instanceId)
    setSkills(list)
    setLoading(false)
  }

  useEffect(() => { reload() /* eslint-disable-line react-hooks/exhaustive-deps */ }, [instanceId])

  const openNew  = () => { setDraft(toDraft(null)); setEditing('new') }
  const openEdit = (s: CustomSkill) => { setDraft(toDraft(s)); setEditing(s.id) }
  const cancel   = () => setEditing(null)

  const save = () => {
    const payload: CustomSkillInput = {
      name:              draft.name.trim(),
      keywords:          parseKeywords(draft.keywordsRaw),
      match_whole_word:  draft.match_whole_word,
      response_template: draft.response_template,
      enabled:           draft.enabled,
    }

    if (!payload.name)                       { toast('Nome é obrigatório.', 'error'); return }
    if (payload.keywords.length === 0)       { toast('Adicione ao menos uma palavra-chave.', 'error'); return }
    if (!payload.response_template.trim())   { toast('Resposta é obrigatória.', 'error'); return }

    startTx(async () => {
      const res = editing === 'new'
        ? await createCustomSkill(instanceId, payload)
        : await updateCustomSkill(instanceId, editing as number, payload)

      if (res.error) {
        toast(res.error, 'error')
      } else {
        toast(editing === 'new' ? 'Skill criada.' : 'Skill atualizada.', 'success')
        cancel()
        reload()
      }
    })
  }

  const remove = (s: CustomSkill) => {
    if (!confirm(`Remover skill "${s.name}"?`)) return
    startTx(async () => {
      const res = await deleteCustomSkill(instanceId, s.id)
      if (res.error) toast(res.error, 'error')
      else { toast('Skill removida.', 'success'); reload() }
    })
  }

  const quickToggle = (s: CustomSkill, next: boolean) => {
    startTx(async () => {
      const res = await updateCustomSkill(instanceId, s.id, { enabled: next })
      if (res.error) toast(res.error, 'error')
      else setSkills(prev => prev.map(x => x.id === s.id ? { ...x, enabled: next } : x))
    })
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-zinc-900 dark:text-white">Custom Skills</h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
            Respostas automáticas por palavra-chave. Suporta <code className="font-mono text-xs">{'{{phone}}'}</code> e <code className="font-mono text-xs">{'{{instance_name}}'}</code> no template.
          </p>
        </div>
        <button
          onClick={openNew}
          disabled={editing !== null}
          className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          Nova skill
        </button>
      </div>

      {editing !== null && (
        <div className="mb-3 p-4 bg-violet-50/40 dark:bg-violet-950/20 rounded-xl border border-violet-200 dark:border-violet-900/40 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Input
              placeholder="Nome da skill (ex: Cardápio)"
              value={draft.name}
              onChange={e => setDraft(d => ({ ...d, name: e.target.value }))}
            />
            <Toggle
              checked={draft.enabled}
              onChange={(next) => setDraft(d => ({ ...d, enabled: next }))}
              ariaLabel="Skill habilitada"
            />
          </div>

          <div>
            <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
              Palavras-chave <span className="text-zinc-400">(separadas por vírgula)</span>
            </label>
            <Input
              placeholder="cardápio, menu, preço"
              value={draft.keywordsRaw}
              onChange={e => setDraft(d => ({ ...d, keywordsRaw: e.target.value }))}
            />
          </div>

          <label className="flex items-center gap-2 text-xs text-zinc-600 dark:text-zinc-400 cursor-pointer">
            <input
              type="checkbox"
              checked={draft.match_whole_word}
              onChange={e => setDraft(d => ({ ...d, match_whole_word: e.target.checked }))}
              className="w-3.5 h-3.5 rounded border-zinc-300 text-violet-600 focus:ring-violet-500"
            />
            Casar apenas palavra inteira (regex <code className="font-mono">\b</code>)
          </label>

          <div>
            <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">Resposta</label>
            <Textarea
              rows={4}
              placeholder="Texto que o bot vai enviar quando alguma keyword bater."
              value={draft.response_template}
              onChange={e => setDraft(d => ({ ...d, response_template: e.target.value }))}
            />
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <button
              onClick={cancel}
              disabled={pending}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded-md border border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              <X className="w-3 h-3" />
              Cancelar
            </button>
            <button
              onClick={save}
              disabled={pending}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded-md bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50 transition-colors"
            >
              <Check className="w-3 h-3" />
              {pending ? 'Salvando…' : 'Salvar'}
            </button>
          </div>
        </div>
      )}

      <div className="flex flex-col gap-1.5">
        {loading && [1, 2].map(i => (
          <div key={i} className="h-16 bg-zinc-100 dark:bg-zinc-800 rounded-xl animate-pulse" />
        ))}

        {!loading && skills.length === 0 && editing === null && (
          <div className="rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 px-6 py-10 text-center bg-white dark:bg-zinc-900">
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Nenhuma custom skill nesta instância. Clique em <span className="font-semibold">Nova skill</span> para criar a primeira.
            </p>
          </div>
        )}

        {skills.map(s => (
          <div
            key={s.id}
            className="flex items-start gap-3 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800"
          >
            <Toggle
              checked={s.enabled}
              onChange={(next) => quickToggle(s, next)}
              ariaLabel={`${s.enabled ? 'Desativar' : 'Ativar'} ${s.name}`}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-zinc-900 dark:text-white">{s.name}</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {s.keywords.map(kw => (
                  <span key={kw} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
                    {kw}
                  </span>
                ))}
                {s.match_whole_word && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-400">
                    \b
                  </span>
                )}
              </div>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1.5 line-clamp-2 leading-relaxed">
                {s.response_template}
              </p>
            </div>
            <div className="flex gap-1 shrink-0">
              <button
                onClick={() => openEdit(s)}
                disabled={editing !== null}
                className="p-1.5 rounded-md text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 disabled:opacity-30 transition-colors"
                title="Editar"
              >
                <Pencil className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => remove(s)}
                disabled={editing !== null}
                className="p-1.5 rounded-md text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 disabled:opacity-30 transition-colors"
                title="Remover"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
