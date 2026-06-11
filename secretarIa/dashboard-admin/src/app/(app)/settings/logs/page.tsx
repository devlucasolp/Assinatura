import { requireAdmin } from '@/lib/auth'
import { LogsClient } from './LogsClient'
import { fetchLogs } from './actions'
import { LOG_SOURCES, LOG_LEVELS } from './constants'

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
