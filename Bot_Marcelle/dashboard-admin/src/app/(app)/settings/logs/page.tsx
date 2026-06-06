import { requireAdmin } from '@/lib/auth'
import { LogsClient } from './LogsClient'
import { fetchLogs, LOG_SOURCES, LOG_LEVELS } from './actions'

export default async function LogsPage() {
  await requireAdmin()
  const initial = await fetchLogs({ tail: 100 })

  return (
    <LogsClient
      initialLogs={initial.logs}
      initialTotal={initial.total}
      sources={LOG_SOURCES}
      levels={LOG_LEVELS}
    />
  )
}
