'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Save } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { useToast } from '@/contexts/ToastContext'
import type { Instance } from '@/types'

type Tab = 'geral' | 'evolution' | 'asana' | 'ia' | 'mensagens'

const TABS: { id: Tab; label: string }[] = [
  { id: 'geral',     label: 'Geral' },
  { id: 'evolution', label: 'WhatsApp' },
  { id: 'asana',     label: 'Asana' },
  { id: 'ia',        label: 'IA' },
  { id: 'mensagens', label: 'Mensagens' },
]

const DEFAULTS: Partial<Instance> = {
  msg_auto_reply_meeting: 'Oi! Estou em reunião no momento.',
  msg_auto_reply_event: 'Oi! Estou em um evento no momento.',
  msg_status_meeting_on: 'Modo Reunião ativado.',
  msg_status_event_on: 'Modo Evento ativado.',
  msg_status_off: 'Modo Desligado.',
  msg_greeting: 'Olá! Como posso ajudar?',
}

export function NewInstanceForm() {
  const router = useRouter()
  const { toast } = useToast()
  const [tab, setTab] = useState<Tab>('geral')
  const [form, setForm] = useState<Partial<Instance>>(DEFAULTS)
  const [saving, setSaving] = useState(false)

  const set = (key: keyof Instance) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(prev => ({ ...prev, [key]: e.target.value }))

  const handleSave = async () => {
    if (!form.id?.trim() || !form.name?.trim() || !form.phone_primary?.trim() || !form.evolution_instance?.trim()) {
      toast('Preencha ID, Nome, Telefone e Instância Evolution.', 'error')
      setTab('geral')
      return
    }
    setSaving(true)
    try {
      const res = await fetch('/api/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || data.error || 'Erro ao criar')
      toast('Instância criada!', 'success')
      router.push(`/instances/${form.id}`)
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : 'Erro ao criar', 'error')
    } finally {
      setSaving(false)
    }
  }

  const field = (label: string, key: keyof Instance, opts?: { type?: string; placeholder?: string; required?: boolean }) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
        {label}{opts?.required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <Input type={opts?.type ?? 'text'} value={(form[key] as string) ?? ''} onChange={set(key)} placeholder={opts?.placeholder} />
    </div>
  )

  const textarea = (label: string, key: keyof Instance, rows = 3) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">{label}</label>
      <Textarea rows={rows} value={(form[key] as string) ?? ''} onChange={set(key)} />
    </div>
  )

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/instances')} className="p-2 rounded-lg text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">Nova instância</h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">Configure um novo bot</p>
          </div>
        </div>
        <Button size="sm" onClick={handleSave} loading={saving}>
          <Save className="w-4 h-4" />
          Criar instância
        </Button>
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800">
        <div className="flex border-b border-zinc-200 dark:border-zinc-800 px-4 gap-1 overflow-x-auto">
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-3.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                tab === t.id
                  ? 'border-violet-600 text-violet-600 dark:border-violet-400 dark:text-violet-400'
                  : 'border-transparent text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {tab === 'geral' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {field('ID da instância', 'id', { placeholder: 'minha-empresa-bot', required: true })}
              {field('Nome de exibição', 'name', { placeholder: 'Bot Empresa X', required: true })}
              {field('Telefone principal', 'phone_primary', { placeholder: '5511999999999', required: true })}
              {field('Telefone secundário', 'phone_secondary', { placeholder: '5511988888888 (opcional)' })}
            </div>
          )}
          {tab === 'evolution' && (
            <div className="grid grid-cols-1 gap-5">
              {field('Instância Evolution', 'evolution_instance', { placeholder: 'gabi-bot', required: true })}
            </div>
          )}
          {tab === 'asana' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {field('Access Token', 'asana_access_token', { type: 'password' })}
              {field('Workspace GID', 'asana_workspace_gid')}
              {field('Project GID', 'asana_project_gid')}
              {field('Section GID', 'asana_section_gid', { placeholder: 'Seção de Reuniões' })}
              {field('User GID', 'asana_user_gid')}
            </div>
          )}
          {tab === 'ia' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {field('Gemini API Key', 'gemini_api_key', { type: 'password' })}
            </div>
          )}
          {tab === 'mensagens' && (
            <div className="flex flex-col gap-5">
              {textarea('Auto-Reply — Modo Reunião', 'msg_auto_reply_meeting')}
              {textarea('Auto-Reply — Modo Evento', 'msg_auto_reply_event')}
              {textarea('Aviso: Modo Reunião ativado', 'msg_status_meeting_on', 2)}
              {textarea('Aviso: Modo Evento ativado', 'msg_status_event_on', 2)}
              {textarea('Aviso: Auto-reply desativado', 'msg_status_off', 2)}
              {textarea('Mensagem de boas-vindas', 'msg_greeting', 5)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
