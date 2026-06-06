import { requireAdmin } from '@/lib/auth'
import { Box } from 'lucide-react'
import { fetchRuns } from './actions'
import { SandboxRunsClient } from './SandboxRunsClient'

export default async function SandboxPage() {
  await requireAdmin()
  const initial = await fetchRuns({ limit: 50 })

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-white flex items-center gap-2">
          <Box className="w-5 h-5 text-violet-500" />
          Sandbox — execuções
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">
          Histórico de execução de código Python por instância. Clique numa linha para ver código + output completos.
        </p>
      </div>

      <SandboxRunsClient initial={initial} />
    </div>
  )
}
