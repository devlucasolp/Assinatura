'use client'

import { useState } from 'react'
import { CheckCircle2, Circle, Users, Bot, ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/contexts/ToastContext'
import { updateInstanceAsana } from './actions'
import type { Instance } from '@/types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type AsanaCreds = {
  asana_access_token: string
  asana_workspace_gid: string
  asana_project_gid: string
  asana_section_gid: string
  asana_user_gid: string
}

type Section = 'conta' | 'instancias' | 'equipe'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function isConfigured(inst: Instance) {
  return !!(inst.asana_access_token?.trim() && inst.asana_workspace_gid?.trim())
}

function deriveSharedCreds(instances: Instance[]): AsanaCreds {
  const configured = instances.find(isConfigured)
  return {
    asana_access_token:  configured?.asana_access_token  ?? '',
    asana_workspace_gid: configured?.asana_workspace_gid ?? '',
    asana_project_gid:   configured?.asana_project_gid   ?? '',
    asana_section_gid:   configured?.asana_section_gid   ?? '',
    asana_user_gid:      configured?.asana_user_gid       ?? '',
  }
}

// ---------------------------------------------------------------------------
// Field primitive
// ---------------------------------------------------------------------------

function F({ label, value, onChange, type = 'text', required, placeholder, description }: {
  label: string; value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  type?: string; required?: boolean; placeholder?: string; description?: string
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <Input type={type} value={value} onChange={onChange} placeholder={placeholder} />
      {description && <p className="mt-1.5 text-xs text-zinc-400 dark:text-zinc-500 leading-relaxed">{description}</p>}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Section toggle wrapper
// ---------------------------------------------------------------------------

function SectionPanel({ icon: Icon, title, subtitle, children, defaultOpen = false }: {
  icon: React.ElementType; title: string; subtitle: string
  children: React.ReactNode; defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 overflow-hidden">
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-zinc-50 dark:hover:bg-zinc-800/40 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center text-zinc-500 dark:text-zinc-400">
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <p className="text-sm font-semibold text-zinc-900 dark:text-white">{title}</p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">{subtitle}</p>
          </div>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-zinc-400 shrink-0" /> : <ChevronDown className="w-4 h-4 text-zinc-400 shrink-0" />}
      </button>
      {open && (
        <div className="border-t border-zinc-100 dark:border-zinc-800 px-5 py-5">
          {children}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Conta section
// ---------------------------------------------------------------------------

function ContaSection({ creds, onChange, onSaveAll, saving, instances }: {
  creds: AsanaCreds
  onChange: (key: keyof AsanaCreds, val: string) => void
  onSaveAll: (selected: string[]) => Promise<void>
  saving: boolean
  instances: Instance[]
}) {
  const [selected, setSelected] = useState<Set<string>>(
    new Set(instances.filter(isConfigured).map(i => i.id))
  )

  const toggle = (id: string) =>
    setSelected(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-4">
        <F label="Personal Access Token" value={creds.asana_access_token} onChange={e => onChange('asana_access_token', e.target.value)} type="password" required description="Gerado em Asana → Configurações → Apps → Personal Access Tokens." />
        <F label="Workspace GID" value={creds.asana_workspace_gid} onChange={e => onChange('asana_workspace_gid', e.target.value)} required description="ID do workspace — encontrado na URL do Asana." />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <F label="Project GID" value={creds.asana_project_gid} onChange={e => onChange('asana_project_gid', e.target.value)} />
        <F label="Section GID" value={creds.asana_section_gid} onChange={e => onChange('asana_section_gid', e.target.value)} placeholder="Seção de Reuniões" />
        <F label="User GID" value={creds.asana_user_gid} onChange={e => onChange('asana_user_gid', e.target.value)} />
      </div>

      {instances.length > 0 && (
        <div>
          <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-3">Aplicar nas instâncias</p>
          <div className="flex flex-col gap-1.5 mb-4">
            {instances.map(inst => (
              <label key={inst.id} className="flex items-center gap-3 px-3 py-2.5 rounded-lg border border-zinc-100 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={selected.has(inst.id)}
                  onChange={() => toggle(inst.id)}
                  className="w-4 h-4 rounded border-zinc-300 text-violet-600 focus:ring-violet-500"
                />
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium text-zinc-900 dark:text-white">{inst.name}</span>
                  <span className="ml-2 text-xs text-zinc-400 dark:text-zinc-500 font-mono">{inst.id}</span>
                </div>
                {isConfigured(inst) && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />}
              </label>
            ))}
          </div>
          <div className="flex justify-end">
            <Button size="sm" onClick={() => onSaveAll(Array.from(selected))} loading={saving} disabled={selected.size === 0}>
              Salvar em {selected.size} instância{selected.size !== 1 ? 's' : ''}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Instâncias section — visão de status por instância
// ---------------------------------------------------------------------------

function InstanciasSection({ instances }: { instances: Instance[] }) {
  if (instances.length === 0) {
    return <p className="text-sm text-zinc-500 dark:text-zinc-400">Nenhuma instância configurada.</p>
  }
  return (
    <div className="flex flex-col gap-2">
      {instances.map(inst => {
        const ok = isConfigured(inst)
        return (
          <div key={inst.id} className="flex items-center justify-between py-2">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-md bg-violet-50 dark:bg-violet-950/50 flex items-center justify-center text-violet-700 dark:text-violet-400 font-semibold text-xs">
                {inst.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-900 dark:text-white">{inst.name}</p>
                <p className="text-xs text-zinc-400 dark:text-zinc-500 font-mono">{inst.id}</p>
              </div>
            </div>
            {ok
              ? <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400"><CheckCircle2 className="w-3.5 h-3.5" />Conectado</span>
              : <span className="flex items-center gap-1.5 text-xs text-zinc-400 dark:text-zinc-500"><Circle className="w-3.5 h-3.5" />Sem credenciais</span>
            }
          </div>
        )
      })}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Equipe section — placeholder até gestão de equipe estar implementada
// ---------------------------------------------------------------------------

function EquipeSection() {
  return (
    <div className="flex flex-col gap-3">
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        Associe membros da equipe a esta conta do Asana para controlar quem pode ver e editar tarefas pelo painel.
      </p>
      <div className="rounded-lg border border-dashed border-zinc-200 dark:border-zinc-700 px-4 py-8 text-center">
        <p className="text-sm text-zinc-400 dark:text-zinc-500">
          Disponível após configurar membros em{' '}
          <a href="/settings/team" className="text-violet-600 dark:text-violet-400 underline underline-offset-2">Configurações → Equipe</a>.
        </p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Root export
// ---------------------------------------------------------------------------

export function AsanaConnectorClient({ instances }: { instances: Instance[] }) {
  const { toast } = useToast()
  const [creds, setCreds] = useState<AsanaCreds>(deriveSharedCreds(instances))
  const [saving, setSaving] = useState(false)

  const handleChange = (key: keyof AsanaCreds, val: string) =>
    setCreds(prev => ({ ...prev, [key]: val }))

  const handleSaveAll = async (selectedIds: string[]) => {
    if (!creds.asana_access_token.trim() || !creds.asana_workspace_gid.trim()) {
      toast('Access Token e Workspace GID são obrigatórios.', 'error'); return
    }
    setSaving(true)
    try {
      const results = await Promise.allSettled(
        selectedIds.map(async id => {
          const res = await updateInstanceAsana(id, creds)
          if (res.error) throw new Error(res.error)
          return res
        })
      )
      const failed = results.filter(r => r.status === 'rejected').length
      if (failed > 0) toast(`${failed} instância(s) falharam ao salvar.`, 'error')
      else toast(`Asana aplicado em ${selectedIds.length} instância${selectedIds.length > 1 ? 's' : ''}!`, 'success')
    } catch {
      toast('Erro ao salvar.', 'error')
    } finally { setSaving(false) }
  }

  const configured = instances.filter(isConfigured)

  return (
    <div className="flex flex-col gap-3">
      {/* Summary badge */}
      {instances.length > 0 && (
        <div className="flex items-center gap-2 mb-2">
          <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${
            configured.length === instances.length
              ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400'
              : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'
          }`}>
            {configured.length === instances.length
              ? <CheckCircle2 className="w-3 h-3" />
              : <Circle className="w-3 h-3" />
            }
            {configured.length}/{instances.length} instâncias conectadas
          </span>
        </div>
      )}

      <SectionPanel
        icon={({ className }: { className?: string }) => <span className={className} style={{ fontSize: '1rem' }}>🔑</span>}
        title="Conta"
        subtitle="Credenciais do workspace Asana compartilhadas com as instâncias selecionadas."
        defaultOpen
      >
        <ContaSection
          creds={creds}
          onChange={handleChange}
          onSaveAll={handleSaveAll}
          saving={saving}
          instances={instances}
        />
      </SectionPanel>

      <SectionPanel icon={Bot} title="Instâncias" subtitle={`${configured.length} de ${instances.length} bots conectados a esta conta.`}>
        <InstanciasSection instances={instances} />
      </SectionPanel>

      <SectionPanel icon={Users} title="Equipe" subtitle="Membros com acesso a esta integração.">
        <EquipeSection />
      </SectionPanel>
    </div>
  )
}
