'use client'

import { useEffect, useState, useTransition } from 'react'
import { RefreshCw, Search } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { fetchLogs, type LogEntry } from './actions'

type Props = {
  initialLogs:  LogEntry[]
  initialTotal: number
  sources:      readonly string[]
  levels:       readonly string[]
}

const LEVEL_BADGE: Record<string, string> = {
  DEBUG:   'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400',
  INFO:    'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400',
  WARNING: 'bg-yellow-50 text-yellow-700 dark:bg-yellow-950/40 dark:text-yellow-400',
  ERROR:   'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-400',
}

const SOURCE_BADGE = 'bg-violet-50 text-violet-700 dark:bg-violet-950/40 dark:text-violet-400'

export function LogsClient({ initialLogs, initialTotal, sources, levels }: Props) {
  const [logs, setLogs]       = useState(initialLogs)
  const [total, setTotal]     = useState(initialTotal)
  const [source, setSource]   = useState('')
  const [level, setLevel]     = useState('')
  const [search, setSearch]   = useState('')
  const [tail, setTail]       = useState(100)
  const [autoRefresh, setAR]  = useState(false)
  const [pending, startTx]    = useTransition()

  const reload = () => {
    startTx(async () => {
      const r = await fetchLogs({ source: source || undefined, level: level || undefined, tail })
      setLogs(r.logs)
      setTotal(r.total)
    })
  }

  // Recarrega quando filtros mudam
  useEffect(() => { reload() /* eslint-disable-line react-hooks/exhaustive-deps */ }, [source, level, tail])

  // Auto-refresh a cada 3s
  useEffect(() => {
    if (!autoRefresh) return
    const id = setInterval(reload, 3000)
    return () => clearInterval(id)
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [autoRefresh, source, level, tail])

  const filtered = search
    ? logs.filter(l => l.msg.toLowerCase().includes(search.toLowerCase()))
    : logs

  const selectCls = 'rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-zinc-900 dark:text-zinc-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400'

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">Logs</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">
            Últimas 500 entradas em memória do bot Python (FastAPI).
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <label className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={e => setAR(e.target.checked)}
              className="w-3.5 h-3.5 rounded border-zinc-300 text-violet-600 focus:ring-violet-500"
            />
            Auto (3s)
          </label>
          <Button size="sm" variant="ghost" onClick={reload} loading={pending}>
            <RefreshCw className="w-4 h-4" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-2 p-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
        <select value={source} onChange={e => setSource(e.target.value)} className={selectCls}>
          <option value="">Todas as fontes</option>
          {sources.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={level} onChange={e => setLevel(e.target.value)} className={selectCls}>
          <option value="">Todos os níveis</option>
          {levels.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
        <select value={tail} onChange={e => setTail(Number(e.target.value))} className={selectCls}>
          <option value={50}>50</option>
          <option value={100}>100</option>
          <option value={250}>250</option>
          <option value={500}>500</option>
        </select>
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-400" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar na mensagem…"
            className={`${selectCls} w-full pl-8`}
          />
        </div>
      </div>

      {/* Tabela */}
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 overflow-hidden">
        <div className="px-4 py-2 border-b border-zinc-100 dark:border-zinc-800 text-xs text-zinc-500 dark:text-zinc-400">
          Mostrando {filtered.length} de {total} entradas
        </div>
        <div className="overflow-auto max-h-[calc(100vh-22rem)]">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 bg-zinc-50 dark:bg-zinc-800/50 text-zinc-500 dark:text-zinc-400 text-xs">
              <tr>
                <th className="px-3 py-2 font-medium w-44">Hora</th>
                <th className="px-3 py-2 font-medium w-20">Nível</th>
                <th className="px-3 py-2 font-medium w-32">Fonte</th>
                <th className="px-3 py-2 font-medium">Mensagem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60 font-mono text-xs">
              {filtered.length === 0 && (
                <tr><td colSpan={4} className="px-3 py-12 text-center text-zinc-400 font-sans">Sem logs.</td></tr>
              )}
              {filtered.slice().reverse().map((l, i) => (
                <tr key={`${l.time}-${i}`} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/30">
                  <td className="px-3 py-1.5 text-zinc-500 dark:text-zinc-500 whitespace-nowrap">{l.time}</td>
                  <td className="px-3 py-1.5">
                    <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold ${LEVEL_BADGE[l.level] ?? LEVEL_BADGE.INFO}`}>
                      {l.level}
                    </span>
                  </td>
                  <td className="px-3 py-1.5">
                    <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold ${SOURCE_BADGE}`}>
                      {l.source.replace('LogSource.', '')}
                    </span>
                  </td>
                  <td className="px-3 py-1.5 text-zinc-700 dark:text-zinc-300 break-all">{l.msg}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
