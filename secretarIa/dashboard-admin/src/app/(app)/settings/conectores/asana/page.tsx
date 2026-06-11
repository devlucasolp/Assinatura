import Link from 'next/link'
import Image from 'next/image'
import { ArrowLeft } from 'lucide-react'
import { requireAdmin } from '@/lib/auth'
import { railsApi } from '@/lib/rails-api'
import { AsanaConnectorClient } from './AsanaConnectorClient'
import type { Instance } from '@/types'

async function fetchInstances(): Promise<Instance[]> {
  try { const r = await railsApi.get('/api/v1/instances'); if (!r.ok) return []; return r.json() }
  catch { return [] }
}

export default async function AsanaConnectorPage() {
  await requireAdmin()
  const instances = await fetchInstances()

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <Link href="/settings/conectores" className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white dark:bg-zinc-800 border border-zinc-100 dark:border-zinc-700 flex items-center justify-center shadow-sm">
            <Image
              src="https://svgl.app/library/asana-logo.svg"
              alt="Asana"
              width={24}
              height={24}
              className="w-6 h-6 object-contain"
              unoptimized
            />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">Asana</h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">Configure e associe o Asana às instâncias e equipe</p>
          </div>
        </div>
      </div>
      <AsanaConnectorClient instances={instances} />
    </div>
  )
}
