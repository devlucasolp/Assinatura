import { requireAuth } from '@/lib/auth'
import { railsApi } from '@/lib/rails-api'
import { InstancesTabs } from './InstancesTabs'
import type { Instance } from '@/types'

async function fetchInstances(): Promise<Instance[]> {
  try {
    const res = await railsApi.get('/api/v1/instances')
    if (!res.ok) return []
    return res.json()
  } catch { return [] }
}

export default async function InstancesPage() {
  await requireAuth()
  const instances = await fetchInstances()
  const wsBase = (process.env.BOT_BACKEND_URL ?? 'http://127.0.0.1:8000').replace(/^http/, 'ws')

  return <InstancesTabs instances={instances} wsBase={wsBase} />
}
