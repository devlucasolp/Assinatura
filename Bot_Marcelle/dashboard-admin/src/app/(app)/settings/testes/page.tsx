import { requireAuth } from '@/lib/auth'
import { api } from '@/lib/api'
import { ChatClient } from './ChatClient'
import type { Instance } from '@/types'

async function fetchInstances(): Promise<Instance[]> {
  try {
    const res = await api.get('/api/instances')
    if (!res.ok) return []
    return res.json()
  } catch { return [] }
}

export default async function TestesPage() {
  await requireAuth()
  const instances = await fetchInstances()
  const wsBase = process.env.BOT_BACKEND_URL?.replace(/^http/, 'ws') ?? 'ws://127.0.0.1:8000'

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4 shrink-0">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">Testes</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">Chat direto com o bot via WebSocket</p>
      </div>
      <ChatClient instances={instances} wsBase={wsBase} />
    </div>
  )
}
