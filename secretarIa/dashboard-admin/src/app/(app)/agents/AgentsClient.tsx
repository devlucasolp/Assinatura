'use client'

import { useState } from 'react'
import { Save, Sparkles, MessageSquare, ChevronDown, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { useToast } from '@/contexts/ToastContext'
import type { Instance } from '@/types'

type Tab = 'ia' | 'mensagens'

const TABS: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: 'ia',        label: 'Inteligência Artificial', icon: Sparkles },
  { id: 'mensagens', label: 'Mensagens Automáticas',   icon: MessageSquare },
]

export function AgentsClient({ instances }: { instances: Instance[] }) {
  const { toast } = useToast()
  const [selectedId, setSelectedId] = useState<string | null>(instances[0]?.id ?? null)
  const [tab, setTab] = useState<Tab>('ia')
  const [saving, setSaving] = useState(false)
  const [forms, setForms] = useState<Record<string, Partial<Instance>>>(() => {
    const map: Record<string, Partial<Instance>> = {}
    instances.forEach(inst => { map[inst.id] = { ...inst } })
    return map
  })

  const current = selectedId ? forms[selectedId] : null

  const set = (key: keyof Instance) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (!selectedId) return
    setForms(prev => ({
      ...prev,
      [selectedId]: { ...prev[selectedId], [key]: e.target.value },
    }))
  }

  const handleSave = async () => {
    if (!selectedId || !current) return
    setSaving(true)
    try {
      const res = await fetch('/api/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(current),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || data.error || 'Erro ao salvar')
      toast('Configurações do agente salvas!', 'success')
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : 'Erro ao salvar', 'error')
    } finally {
      setSaving(false)
    }
  }

  if (instances.length === 0) {
    return (
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-8 text-center">
        <Sparkles className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Nenhuma instância disponível. Crie uma instância primeiro.</p>
      </div>
    )
  }

  const field = (label: string, key: keyof Instance, opts?: { type?: string; placeholder?: string; description?: string }) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">{label}</label>
      <Input
        type={opts?.type ?? 'text'}
        value={(current?.[key] as string) ?? ''}
        onChange={set(key)}
        placeholder={opts?.placeholder}
      />
      {opts?.description && (
        <p className="text-xs text-zinc-400 dark:text-zinc-500">{opts.description}</p>
      )}
    </div>
  )

  const textarea = (label: string, key: keyof Instance, rows = 3, description?: string) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">{label}</label>
      <Textarea rows={rows} value={(current?.[key] as string) ?? ''} onChange={set(key)} />
      {description && (
        <p className="text-xs text-zinc-400 dark:text-zinc-500">{description}</p>
      )}
    </div>
  )

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Instance Selector (left panel) */}
      <div className="lg:w-56 shrink-0 space-y-1">
        <p className="text-xs font-medium text-zinc-400 dark:text-zinc-500 uppercase tracking-wide mb-2 px-1">Instância</p>
        {instances.map(inst => (
          <button
            key={inst.id}
            onClick={() => setSelectedId(inst.id)}
            className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              selectedId === inst.id
                ? 'bg-violet-50 text-violet-700 dark:bg-violet-900/20 dark:text-violet-400'
                : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800'
            }`}
          >
            <div className="w-6 h-6 rounded bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center text-violet-700 dark:text-violet-400 font-semibold text-xs shrink-0">
              {inst.name.charAt(0).toUpperCase()}
            </div>
            <span className="truncate">{inst.name}</span>
            {selectedId === inst.id && <ChevronRight className="w-3 h-3 ml-auto shrink-0" />}
          </button>
        ))}
      </div>

      {/* Editor (right panel) */}
      {current && (
        <div className="flex-1 space-y-5">
          {/* Tabs */}
          <div className="flex items-center justify-between">
            <div className="flex border-b border-zinc-200 dark:border-zinc-800 gap-1">
              {TABS.map(t => {
                const Icon = t.icon
                return (
                  <button
                    key={t.id}
                    onClick={() => setTab(t.id)}
                    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                      tab === t.id
                        ? 'border-violet-600 text-violet-600 dark:border-violet-400 dark:text-violet-400'
                        : 'border-transparent text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {t.label}
                  </button>
                )
              })}
            </div>
            <Button size="sm" onClick={handleSave} loading={saving}>
              <Save className="w-4 h-4" />
              Salvar
            </Button>
          </div>

          {/* Content */}
          <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
            {tab === 'ia' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Chaves de API</h3>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Chaves de acesso para os modelos de linguagem utilizados pelo agente.</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {field('Gemini API Key', 'gemini_api_key', { type: 'password', description: 'Chave da API do Google Gemini.' })}
                    {field('OpenAI API Key', 'openai_api_key', { type: 'password', description: 'Chave da API da OpenAI.' })}
                  </div>
                </div>
                <hr className="border-zinc-200 dark:border-zinc-800" />
                <div>
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Modelo</h3>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Modelo de IA utilizado nas respostas do agente.</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {field('Modelo OpenAI', 'openai_model', { placeholder: 'gpt-4o', description: 'Ex: gpt-4o, gpt-4o-mini, gpt-3.5-turbo' })}
                  </div>
                </div>
              </div>
            )}

            {tab === 'mensagens' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Auto-Reply</h3>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Mensagens enviadas automaticamente quando um modo está ativado.</p>
                  <div className="flex flex-col gap-4">
                    {textarea('Modo Reunião', 'msg_auto_reply_meeting', 3, 'Resposta automática quando o bot está em modo reunião.')}
                    {textarea('Modo Evento', 'msg_auto_reply_event', 3, 'Resposta automática quando o bot está em modo evento.')}
                  </div>
                </div>
                <hr className="border-zinc-200 dark:border-zinc-800" />
                <div>
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Avisos de Status</h3>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Mensagens enviadas ao operador quando um modo é ativado ou desativado.</p>
                  <div className="flex flex-col gap-4">
                    {textarea('Reunião ativada', 'msg_status_meeting_on', 2, 'Aviso exibido ao ativar o modo reunião.')}
                    {textarea('Evento ativado', 'msg_status_event_on', 2, 'Aviso exibido ao ativar o modo evento.')}
                    {textarea('Auto-reply desativado', 'msg_status_off', 2, 'Aviso exibido ao desligar qualquer modo.')}
                  </div>
                </div>
                <hr className="border-zinc-200 dark:border-zinc-800" />
                <div>
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Boas-vindas</h3>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Mensagem enviada quando um novo contato inicia a conversa.</p>
                  {textarea('Mensagem de boas-vindas', 'msg_greeting', 5, 'Primeira mensagem que o bot envia ao ser contatado.')}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
