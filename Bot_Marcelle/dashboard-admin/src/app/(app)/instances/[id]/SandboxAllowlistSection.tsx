'use client'

import { useEffect, useState, useTransition } from 'react'
import { Plus, Trash2, Globe } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/contexts/ToastContext'
import { fetchAllowlist, addAllowlist, removeAllowlist, type AllowlistEntry } from './sandbox-allowlist-actions'

export function SandboxAllowlistSection({ instanceId }: { instanceId: string }) {
  const { toast }              = useToast()
  const [entries, setEntries]  = useState<AllowlistEntry[]>([])
  const [loading, setLoading]  = useState(true)
  const [host, setHost]        = useState('')
  const [note, setNote]        = useState('')
  const [pending, startTx]     = useTransition()

  const reload = async () => {
    const list = await fetchAllowlist(instanceId)
    setEntries(list)
    setLoading(false)
  }

  useEffect(() => { reload() /* eslint-disable-line react-hooks/exhaustive-deps */ }, [instanceId])

  const add = () => {
    if (!host.trim()) return
    startTx(async () => {
      const res = await addAllowlist(instanceId, host.trim(), note.trim() || undefined)
      if (res.error) {
        toast(res.error, 'error')
      } else {
        toast('Host adicionado.', 'success')
        setHost(''); setNote(''); reload()
      }
    })
  }

  const remove = (e: AllowlistEntry) => {
    if (!confirm(`Remover "${e.host_pattern}" da allow-list?`)) return
    startTx(async () => {
      const res = await removeAllowlist(instanceId, e.id)
      if (res.error) toast(res.error, 'error')
      else { toast('Removido.', 'success'); reload() }
    })
  }

  return (
    <section>
      <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1 flex items-center gap-2">
        <Globe className="w-4 h-4 text-zinc-400" />
        Sandbox — hosts HTTP permitidos
      </h3>
      <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">
        Domínios que o código executado na sandbox pode acessar. Use <code className="font-mono text-xs">*.exemplo.com</code> para liberar todos os subdomínios. Sem entradas = sandbox sem rede.
      </p>

      <div className="flex flex-col gap-2 p-4 bg-violet-50/40 dark:bg-violet-950/20 rounded-xl border border-violet-200 dark:border-violet-900/40 mb-3">
        <div className="grid grid-cols-2 gap-2">
          <Input
            placeholder="api.openai.com ou *.openai.com"
            value={host}
            onChange={e => setHost(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') add() }}
          />
          <Input
            placeholder="Anotação (opcional)"
            value={note}
            onChange={e => setNote(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') add() }}
          />
        </div>
        <div className="flex justify-end">
          <Button size="sm" onClick={add} loading={pending} disabled={!host.trim()}>
            <Plus className="w-4 h-4" />
            Adicionar host
          </Button>
        </div>
      </div>

      {loading
        ? <div className="h-12 bg-zinc-100 dark:bg-zinc-800 rounded-xl animate-pulse" />
        : entries.length === 0
          ? <div className="rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 px-6 py-8 text-center bg-white dark:bg-zinc-900">
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Sem hosts permitidos. A sandbox desta instância está em <span className="font-semibold">modo offline</span>.
              </p>
            </div>
          : <div className="flex flex-col gap-1.5">
              {entries.map(e => (
                <div key={e.id} className="flex items-center gap-3 px-4 py-2.5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-mono text-zinc-900 dark:text-white">{e.host_pattern}</p>
                    {e.note && <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">{e.note}</p>}
                  </div>
                  <button
                    onClick={() => remove(e)}
                    disabled={pending}
                    className="p-1.5 rounded-md text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 disabled:opacity-30 transition-colors"
                    title="Remover"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
      }
    </section>
  )
}
