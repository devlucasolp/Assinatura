'use client'

import { useEffect, useState, useTransition } from 'react'
import { X, RefreshCw, CheckCircle2, AlertCircle, Skull } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { fetchRuns, fetchRunFull, type SandboxRun, type SandboxRunFull, type RunsResponse } from './actions'

const STATUS_OPTS = [
  { value: '',         label: 'Todos' },
  { value: 'success',  label: 'Sucesso' },
  { value: 'error',    label: 'Erro' },
  { value: 'killed',   label: 'Killed' },
] as const

function formatDur(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const s = Math.floor(diff / 1000)
  if (s < 60) return `${s}s atrás`
  if (s < 3600) return `${Math.floor(s / 60)}min atrás`
  if (s < 86400) return `${Math.floor(s / 3600)}h atrás`
  return new Date(iso).toLocaleDateString('pt-BR')
}

function StatusIcon({ run }: { run: SandboxRun }) {
  if (run.killed) return <Skull className="w-4 h-4 text-red-500" />
  if (run.exit_code === 0) return <CheckCircle2 className="w-4 h-4 text-emerald-500" />
  return <AlertCircle className="w-4 h-4 text-amber-500" />
}

export function SandboxRunsClient({ initial }: { initial: RunsResponse }) {
  const [data, setData]         = useState(initial)
  const [instance, setInstance] = useState('')
  const [status, setStatus]     = useState<string>('')
  const [pending, startTx]      = useTransition()
  const [open, setOpen]         = useState<SandboxRunFull | null>(null)

  const reload = (offset = 0) => {
    startTx(async () => {
      const filters: Parameters<typeof fetchRuns>[0] = { offset, limit: 50 }
      if (instance) filters.instance_id = instance
      if (status)   filters.status      = status as 'success' | 'error' | 'killed'
      const r = await fetchRuns(filters)
      setData(r)
    })
  }

  useEffect(() => { reload(0) /* eslint-disable-line react-hooks/exhaustive-deps */ }, [instance, status])

  const showDetail = (id: number) => {
    startTx(async () => {
      const full = await fetchRunFull(id)
      if (full) setOpen(full)
    })
  }

  const selectCls = 'rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-zinc-900 dark:text-zinc-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400'

  return (
    <>
      <div className="flex flex-wrap gap-2 p-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
        <input
          placeholder="Filtrar por instância (ID exato)"
          value={instance}
          onChange={e => setInstance(e.target.value)}
          className={`${selectCls} flex-1 min-w-[200px]`}
        />
        <select value={status} onChange={e => setStatus(e.target.value)} className={selectCls}>
          {STATUS_OPTS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <Button size="sm" variant="ghost" onClick={() => reload(0)} loading={pending}>
          <RefreshCw className="w-4 h-4" />
          Atualizar
        </Button>
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 overflow-hidden">
        <div className="px-4 py-2 border-b border-zinc-100 dark:border-zinc-800 text-xs text-zinc-500 dark:text-zinc-400">
          {data.total} execuções · mostrando {data.offset + 1}-{data.offset + data.runs.length}
        </div>
        <div className="overflow-auto max-h-[calc(100vh-22rem)]">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 bg-zinc-50 dark:bg-zinc-800/50 text-zinc-500 dark:text-zinc-400 text-xs">
              <tr>
                <th className="px-3 py-2 font-medium w-10"></th>
                <th className="px-3 py-2 font-medium">Instância</th>
                <th className="px-3 py-2 font-medium">Origem</th>
                <th className="px-3 py-2 font-medium">Exit</th>
                <th className="px-3 py-2 font-medium">Duração</th>
                <th className="px-3 py-2 font-medium">RAM pico</th>
                <th className="px-3 py-2 font-medium">Kill</th>
                <th className="px-3 py-2 font-medium">Quando</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
              {data.runs.length === 0 && (
                <tr><td colSpan={8} className="px-3 py-12 text-center text-zinc-400">Sem execuções.</td></tr>
              )}
              {data.runs.map(r => (
                <tr
                  key={r.id}
                  onClick={() => showDetail(r.id)}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-800/30 cursor-pointer"
                >
                  <td className="px-3 py-2"><StatusIcon run={r} /></td>
                  <td className="px-3 py-2 font-mono text-xs text-zinc-700 dark:text-zinc-300">{r.instance_id}</td>
                  <td className="px-3 py-2 text-xs">
                    <span className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
                      {r.origin ?? '—'}
                    </span>
                  </td>
                  <td className="px-3 py-2 font-mono text-xs">{r.exit_code}</td>
                  <td className="px-3 py-2 text-xs text-zinc-600 dark:text-zinc-400">{formatDur(r.duration_ms)}</td>
                  <td className="px-3 py-2 text-xs text-zinc-600 dark:text-zinc-400">
                    {r.memory_peak_mb != null ? `${r.memory_peak_mb} MB` : '—'}
                  </td>
                  <td className="px-3 py-2 text-xs text-zinc-600 dark:text-zinc-400">{r.kill_reason ?? '—'}</td>
                  <td className="px-3 py-2 text-xs text-zinc-500">{timeAgo(r.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {data.total > data.runs.length && (
          <div className="px-4 py-2 border-t border-zinc-100 dark:border-zinc-800 flex justify-between items-center">
            <Button size="sm" variant="ghost" disabled={data.offset === 0 || pending}
                    onClick={() => reload(Math.max(0, data.offset - data.limit))}>
              ← Anteriores
            </Button>
            <span className="text-xs text-zinc-500">
              Página {Math.floor(data.offset / data.limit) + 1} de {Math.ceil(data.total / data.limit)}
            </span>
            <Button size="sm" variant="ghost"
                    disabled={data.offset + data.runs.length >= data.total || pending}
                    onClick={() => reload(data.offset + data.limit)}>
              Próximas →
            </Button>
          </div>
        )}
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setOpen(null)}>
          <div
            className="w-full max-w-4xl max-h-[85vh] bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-xl flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-200 dark:border-zinc-800 shrink-0">
              <div className="flex items-center gap-3">
                <StatusIcon run={open} />
                <div>
                  <h2 className="font-semibold text-zinc-900 dark:text-white">Run #{open.id}</h2>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 font-mono">
                    {open.instance_id} · exit {open.exit_code} · {formatDur(open.duration_ms)}
                    {open.memory_peak_mb != null && ` · ${open.memory_peak_mb}MB`}
                    {open.killed && ` · killed (${open.kill_reason})`}
                  </p>
                </div>
              </div>
              <button onClick={() => setOpen(null)} className="p-1 rounded-md text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="overflow-auto p-5 space-y-4 flex-1">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-1">Código</p>
                <pre className="bg-zinc-50 dark:bg-zinc-950 border border-zinc-100 dark:border-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-700 dark:text-zinc-300 overflow-auto whitespace-pre-wrap">{open.code}</pre>
              </div>
              {open.stdout && (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-1">stdout</p>
                  <pre className="bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30 rounded-lg p-3 text-xs font-mono text-emerald-900 dark:text-emerald-200 overflow-auto whitespace-pre-wrap">{open.stdout}</pre>
                </div>
              )}
              {open.stderr && (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-1">stderr</p>
                  <pre className="bg-red-50/50 dark:bg-red-950/20 border border-red-100 dark:border-red-900/30 rounded-lg p-3 text-xs font-mono text-red-900 dark:text-red-300 overflow-auto whitespace-pre-wrap">{open.stderr}</pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
