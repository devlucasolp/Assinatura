import { requireAuth } from '@/lib/auth'
import { api } from '@/lib/api'
import { AgentsClient } from './AgentsClient'
import type { Instance } from '@/types'

async function fetchInstances(): Promise<Instance[]> {
  try {
    const res = await api.get('/api/instances')
    if (!res.ok) return []
    return res.json()
  } catch { return [] }
}

export default async function AgentsPage() {
  await requireAuth()
  const instances = await fetchInstances()

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">Agentes</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">Configure a inteligência artificial e mensagens automáticas de cada instância</p>
      </div>
      <AgentsClient instances={instances} />
    </div>
  )
}
