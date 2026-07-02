'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Trash2, Save, Settings2, Sparkles, MessageSquare, Puzzle, Zap, QrCode, X, Database } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Toggle } from '@/components/ui/Toggle'
import { useToast } from '@/contexts/ToastContext'
import { SkillsTab } from './SkillsTab'
import { CustomSkillsSection } from './CustomSkillsSection'
import { SandboxAllowlistSection } from './SandboxAllowlistSection'
import type { Instance } from '@/types'
import { EvolutionTab } from './EvolutionTab'
import { createAndGetQrCode } from './actions'
import { ScheduledTasksTab } from './ScheduledTasksTab'
import { WebhooksTab } from './WebhooksTab'

type Tab = 'geral' | 'whatsapp' | 'persona' | 'mensagens' | 'skills' | 'automacoes' | 'contexto'

const TABS: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: 'geral',      label: 'Geral',      icon: Settings2 },
  { id: 'whatsapp',   label: 'WhatsApp',   icon: QrCode },
  { id: 'persona',    label: 'Persona',    icon: Sparkles },
  { id: 'mensagens',  label: 'Mensagens',  icon: MessageSquare },
  { id: 'skills',     label: 'Skills',     icon: Puzzle },
  { id: 'automacoes', label: 'Automações', icon: Zap },
  { id: 'contexto',   label: 'Contexto',   icon: Database },
]

type FieldOpts = { type?: string; placeholder?: string; required?: boolean; disabled?: boolean; description?: string; span?: 'full' | 'half' }

export function InstanceEditor({ instance }: { instance: Instance | null }) {
  const router = useRouter()
  const { toast } = useToast()
  const isNew = !instance
  const [tab, setTab] = useState<Tab>('geral')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  
  const [qrModalOpen, setQrModalOpen] = useState(false)
  const [qrCodeBase64, setQrCodeBase64] = useState<string | null>(null)
  const [qrLoading, setQrLoading] = useState(false)
  const [qrError, setQrError] = useState<string | null>(null)

  const [form, setForm] = useState<Partial<Instance>>(instance ?? {
    msg_auto_reply_meeting: 'Oi! Estou em reunião no momento.',
    msg_auto_reply_event: 'Oi! Estou em um evento no momento.',
    msg_status_meeting_on: 'Modo Reunião ativado.',
    msg_status_event_on: 'Modo Evento ativado.',
    msg_status_off: 'Modo Desligado.',
    msg_greeting: 'Olá! Como posso ajudar?',
  })

  const set = (key: keyof Instance) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(prev => ({ ...prev, [key]: e.target.value }))

  const handleSave = async () => {
    if (!form.id?.trim() || !form.name?.trim() || !form.phone_primary?.trim()) {
      toast('Preencha ID, Nome e Telefone.', 'error'); setTab('geral'); return
    }
    if (!form.evolution_instance?.trim()) {
      toast('Preencha a Instância Evolution.', 'error'); setTab('geral'); return
    }
    setSaving(true)
    try {
      const res = isNew
        ? await fetch('/api/instances', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
        : await fetch(`/api/instances/${instance!.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || data.error || 'Erro ao salvar')
      toast('Salvo!', 'success')
      if (isNew) router.push(`/instances/${data.instance?.id ?? data.id}`)
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : 'Erro ao salvar', 'error')
    } finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!instance || !confirm(`Deletar "${instance.id}"?`)) return
    setDeleting(true)
    try {
      const res = await fetch(`/api/instances/${instance.id}`, { method: 'DELETE' })
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail || 'Erro') }
      toast('Deletado.', 'success')
      router.push('/instances')
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : 'Erro ao deletar', 'error')
      setDeleting(false)
    }
  }

  const handleGenerateQr = async () => {
    if (!instance?.id) {
      toast('Salve a instância antes de gerar o QR Code.', 'error')
      return
    }
    setQrModalOpen(true)
    setQrLoading(true)
    setQrError(null)
    setQrCodeBase64(null)
    
    try {
      const data = await createAndGetQrCode(instance.id)
      // Evolution v1: data.base64 | Evolution v2: data.qrcode?.base64
      const base64 = data.base64 || data.qrcode?.base64
      if (base64) {
        setQrCodeBase64(base64.startsWith('data:image') ? base64 : `data:image/png;base64,${base64}`)
      } else {
        setQrError('QR Code não retornado (a instância já pode estar conectada).')
      }
    } catch (e: unknown) {
      setQrError(e instanceof Error ? e.message : 'Erro desconhecido.')
    } finally {
      setQrLoading(false)
    }
  }

  const F = (label: string, key: keyof Instance, opts: FieldOpts = {}) => (
    <div className={opts.span === 'full' ? 'col-span-full' : ''}>
      <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
        {label}
        {opts.required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <Input
        type={opts.type ?? 'text'}
        value={(form[key] as string) ?? ''}
        onChange={set(key)}
        placeholder={opts.placeholder}
        disabled={opts.disabled}
      />
      {opts.description && (
        <p className="mt-1.5 text-xs text-zinc-400 dark:text-zinc-500 leading-relaxed">{opts.description}</p>
      )}
    </div>
  )

  const T = (label: string, key: keyof Instance, rows = 3, description?: string) => (
    <div>
      <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">{label}</label>
      <Textarea rows={rows} value={(form[key] as string) ?? ''} onChange={set(key)} />
      {description && <p className="mt-1.5 text-xs text-zinc-400 dark:text-zinc-500">{description}</p>}
    </div>
  )

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Link href="/instances" className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">
              {isNew ? 'Nova instância' : instance.name}
            </h1>
            {!isNew && <p className="text-sm text-zinc-400 dark:text-zinc-500 font-mono mt-0.5">{instance.id}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!isNew && (
            <Button variant="ghost" size="sm" onClick={handleDelete} loading={deleting} className="text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600">
              <Trash2 className="w-4 h-4" />
              Deletar
            </Button>
          )}
          <Button size="sm" onClick={handleSave} loading={saving}>
            <Save className="w-4 h-4" />
            Salvar alterações
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-0.5 border-b border-zinc-200 dark:border-zinc-800 mb-8 overflow-x-auto">
        {TABS.map(t => {
          const Icon = t.icon
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg border-b-2 -mb-px transition-colors whitespace-nowrap ${
                tab === t.id
                  ? 'border-zinc-900 dark:border-white text-zinc-900 dark:text-white'
                  : 'border-transparent text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {t.label}
            </button>
          )
        })}
      </div>

      {/* Content */}
      <div className="max-w-2xl">
        {tab === 'geral' && (
          <div className="flex flex-col gap-8">
            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Identificação</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Quem é esse bot e como o sistema o referencia.</p>
              <div className="grid grid-cols-2 gap-x-6 gap-y-6">
                {F('ID da instância', 'id', { placeholder: 'minha-empresa-bot', required: true, disabled: !isNew, description: 'Slug único. Não pode ser alterado após criação.' })}
                {F('Nome de exibição', 'name', { placeholder: 'Bot Empresa X', required: true })}
              </div>
            </section>

            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Conexão</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Número do dono e instância na Evolution API.</p>
              <div className="grid grid-cols-2 gap-x-6 gap-y-6">
                {F('Telefone principal', 'phone_primary', { placeholder: '5511999999999', required: true, description: 'Número autorizado a comandar o bot, com DDI e DDD.' })}
                {F('Telefone secundário', 'phone_secondary', { placeholder: '5511988888888', description: 'Opcional. Segundo número autorizado.' })}
                {F('Instância Evolution', 'evolution_instance', { placeholder: 'gabi-dev', required: true, span: 'full', description: 'Deve ser idêntico ao nome cadastrado na Evolution API.' })}
              </div>
            </section>

            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Chaves de IA</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Credenciais usadas pelos modelos deste bot.</p>
              <div className="grid grid-cols-2 gap-x-6 gap-y-6">
                {F('Gemini API Key', 'gemini_api_key', { type: 'password', span: 'full' })}
              </div>
            </section>
          </div>
        )}

        {tab === 'whatsapp' && (
          isNew 
          ? <div className="rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 px-6 py-12 text-center bg-white dark:bg-zinc-900">
              <QrCode className="w-7 h-7 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Salve a instância na aba Geral primeiro.</p>
            </div>
          : <EvolutionTab instance={form as Instance} onChange={(k, v) => setForm(prev => ({ ...prev, [k]: v }))} />
        )}

        {tab === 'persona' && (
          <div className="flex flex-col gap-8">
            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Identidade da assistente</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Nome que o bot usa para se apresentar nas conversas.</p>
              <div className="max-w-md">
                {F('Nome da assistente', 'assistant_name', { placeholder: 'Fernanda', description: 'Vazio = usa o padrão definido no sistema.' })}
              </div>
            </section>

            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">System prompt</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">
                Instrução que define personalidade, tom e regras. É enviada ao Gemini no início de toda conversa.
              </p>
              <Textarea
                rows={20}
                value={(form.system_prompt as string) ?? ''}
                onChange={set('system_prompt')}
                placeholder={'Ex: Você é a Fernanda, secretária executiva da Gabriela...\n\nUse linguagem profissional, direta, sem rodeios.\n\nNUNCA invente dados ou links.'}
                className="font-mono text-xs leading-relaxed"
              />
              <p className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
                Vazio = usa o prompt padrão da Fernanda. Mudanças entram em vigor na próxima mensagem recebida.
              </p>
            </section>
          </div>
        )}

        {tab === 'mensagens' && (
          <div className="flex flex-col gap-7">
            <p className="text-xs text-zinc-500 dark:text-zinc-400 -mt-2">
              Textos que o bot envia em situações específicas. Deixe vazio para usar o padrão do sistema.
            </p>
            <div className="grid grid-cols-2 gap-x-6 gap-y-6">
              {T('Auto-reply — modo reunião', 'msg_auto_reply_meeting', 2)}
              {T('Auto-reply — modo evento', 'msg_auto_reply_event', 2)}
            </div>
            <div className="grid grid-cols-3 gap-4">
              {T('Aviso: reunião ativada', 'msg_status_meeting_on', 2)}
              {T('Aviso: evento ativado', 'msg_status_event_on', 2)}
              {T('Aviso: modo desligado', 'msg_status_off', 2)}
            </div>
            {T('Mensagem de boas-vindas', 'msg_greeting', 5, 'Enviada quando o usuário manda "oi" pela primeira vez.')}
          </div>
        )}

        {tab === 'skills' && (
          isNew
            ? <div className="rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 px-6 py-12 text-center bg-white dark:bg-zinc-900">
                <Puzzle className="w-7 h-7 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                  Salve a instância primeiro para configurar as skills.
                </p>
              </div>
            : <div className="flex flex-col gap-10">
                <SkillsTab instanceId={instance.id} />
                <div className="border-t border-zinc-100 dark:border-zinc-800" />
                <CustomSkillsSection instanceId={instance.id} />
              </div>
        )}

        {tab === 'automacoes' && (
          <div className="flex flex-col gap-8">
            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Briefings diários do Asana</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">
                O bot envia automaticamente um resumo das tarefas no horário escolhido. Deixe vazio para desligar.
              </p>

              <div className="flex flex-col gap-2">
                {([
                  { key: 'briefing_morning'   as const, label: 'Manhã',     default: '10:00', help: 'Resumo com tarefas atrasadas + a fazer hoje.' },
                  { key: 'briefing_afternoon' as const, label: 'Meio-dia',  default: '15:00', help: 'O que ainda está aberto para hoje.' },
                  { key: 'briefing_evening'   as const, label: 'Fim do dia', default: '18:00', help: 'O que sobrou para revisar ou remarcar.' },
                ]).map(({ key, label, default: defaultTime, help }) => {
                  const current = (form[key] as string | null | undefined) ?? null
                  const enabled = !!current
                  return (
                    <div key={key} className="flex items-center gap-4 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
                      <Toggle
                        checked={enabled}
                        onChange={(next) => setForm(prev => ({ ...prev, [key]: next ? defaultTime : null }))}
                        ariaLabel={`Ativar briefing ${label}`}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-zinc-900 dark:text-white">{label}</p>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">{help}</p>
                      </div>
                      <input
                        type="time"
                        value={current ?? ''}
                        disabled={!enabled}
                        onChange={e => setForm(prev => ({ ...prev, [key]: e.target.value }))}
                        className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-zinc-900 dark:text-zinc-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 disabled:opacity-40 disabled:cursor-not-allowed"
                      />
                    </div>
                  )
                })}
              </div>
            </section>

            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Novas tarefas no Asana</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">
                Avisa por WhatsApp quando aparecem tarefas novas atribuídas. Deixe vazio para desligar.
              </p>

              <div className="flex items-center gap-4 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
                <Toggle
                  checked={!!form.new_tasks_poll_minutes}
                  onChange={(next) => setForm(prev => ({ ...prev, new_tasks_poll_minutes: next ? 10 : null }))}
                  ariaLabel="Ativar polling de novas tarefas"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-zinc-900 dark:text-white">Polling de novas tarefas</p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">Verifica a cada X minutos.</p>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={1}
                    max={1440}
                    value={form.new_tasks_poll_minutes ?? ''}
                    disabled={!form.new_tasks_poll_minutes}
                    onChange={e => {
                      const v = e.target.value
                      setForm(prev => ({ ...prev, new_tasks_poll_minutes: v ? Number(v) : null }))
                    }}
                    className="w-20 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-zinc-900 dark:text-zinc-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 disabled:opacity-40"
                  />
                  <span className="text-xs text-zinc-500 dark:text-zinc-400">min</span>
                </div>
              </div>
            </section>

            <section>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Fuso horário</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">Base para os horários acima.</p>
              <div className="max-w-xs">
                {F('Timezone', 'briefing_timezone', { placeholder: 'America/Sao_Paulo', description: 'Formato IANA. Ex: America/Sao_Paulo, America/New_York.' })}
              </div>
            </section>

            {!isNew && (
              <>
                <div className="border-t border-zinc-100 dark:border-zinc-800" />
                <SandboxAllowlistSection instanceId={instance.id} />

                <div className="border-t border-zinc-100 dark:border-zinc-800" />
                <section>
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Agendamentos e webhooks (legado)</h3>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">
                    Criados pela IA no modelo antigo. Serão substituídos pela nova UI unificada de automações.
                  </p>
                  <div className="flex flex-col gap-8">
                    <ScheduledTasksTab instanceId={instance.id} />
                    <WebhooksTab instanceId={instance.id} />
                  </div>
                </section>
              </>
            )}
          </div>
        )}

        {tab === 'contexto' && (
          isNew
            ? <div className="rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 px-6 py-12 text-center bg-white dark:bg-zinc-900">
                <Database className="w-7 h-7 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
                <p className="text-sm text-zinc-500 dark:text-zinc-400">Salve a instância primeiro para ver o contexto.</p>
              </div>
            : <div className="rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 px-6 py-16 text-center bg-white dark:bg-zinc-900">
                <Database className="w-7 h-7 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
                <p className="text-sm text-zinc-500 dark:text-zinc-400">Editor de estado da instância — em construção.</p>
              </div>
        )}
      </div>


    </div>
  )
}
