'use client'

import { useState } from 'react'
import { X, Copy, Check, Mail } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/contexts/ToastContext'
import { createInvite, type Invite } from './actions'

type Props = {
  onClose: () => void
}

export function InviteModal({ onClose }: Props) {
  const { toast }                 = useToast()
  const [email, setEmail]         = useState('')
  const [role, setRole]           = useState<'admin' | 'viewer'>('viewer')
  const [submitting, setSubmitting] = useState(false)
  const [invite, setInvite]       = useState<Invite | null>(null)
  const [copied, setCopied]       = useState(false)

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    setSubmitting(true)
    const res = await createInvite(email.trim(), role)
    setSubmitting(false)

    if (res.error) {
      toast(res.error, 'error')
      return
    }
    setInvite(res.invite!)
  }

  const inviteUrl = invite
    ? `${typeof window !== 'undefined' ? window.location.origin : ''}/register?token=${invite.token}`
    : ''

  const handleCopy = async () => {
    await navigator.clipboard.writeText(inviteUrl)
    setCopied(true)
    toast('Link copiado.', 'success')
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div
        className="w-full max-w-md bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-xl"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="font-semibold text-zinc-900 dark:text-white">
            {invite ? 'Convite criado' : 'Convidar usuário'}
          </h2>
          <button onClick={onClose} className="p-1 rounded-md text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {!invite ? (
          <form onSubmit={handleCreate} className="p-5 flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">E-mail do convidado</label>
              <Input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="pessoa@empresa.com"
                required
                autoFocus
              />
              <p className="text-xs text-zinc-400 dark:text-zinc-500">
                Convites permitem registro fora do domínio @assinaturamarcapropria.com.br.
              </p>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Papel</label>
              <select
                value={role}
                onChange={e => setRole(e.target.value as 'admin' | 'viewer')}
                className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-zinc-900 dark:text-zinc-100 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400"
              >
                <option value="viewer">Visualizador</option>
                <option value="admin">Administrador</option>
              </select>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
              <Button type="submit" loading={submitting}>
                <Mail className="w-4 h-4" />
                Gerar convite
              </Button>
            </div>
          </form>
        ) : (
          <div className="p-5 flex flex-col gap-4">
            <div className="text-sm">
              <p className="text-zinc-700 dark:text-zinc-300">
                Convite criado para <span className="font-semibold">{invite.email}</span> como{' '}
                <span className="font-semibold">{invite.role === 'admin' ? 'Administrador' : 'Visualizador'}</span>.
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                Expira em {new Date(invite.expires_at).toLocaleString('pt-BR')}
              </p>
            </div>

            <div>
              <label className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                Link de registro
              </label>
              <div className="mt-1.5 flex items-stretch gap-2">
                <input
                  readOnly
                  value={inviteUrl}
                  onFocus={e => e.target.select()}
                  className="flex-1 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 text-xs font-mono text-zinc-700 dark:text-zinc-300 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-violet-500/25"
                />
                <Button onClick={handleCopy} variant={copied ? 'ghost' : 'primary'}>
                  {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copiado' : 'Copiar'}
                </Button>
              </div>
              <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-2">
                Envie este link para o convidado por WhatsApp, e-mail ou outro canal seguro.
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <Button onClick={onClose}>Pronto</Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
