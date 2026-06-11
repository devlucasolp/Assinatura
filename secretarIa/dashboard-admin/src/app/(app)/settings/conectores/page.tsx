import Link from 'next/link'
import Image from 'next/image'
import { requireAdmin } from '@/lib/auth'
import { railsApi } from '@/lib/rails-api'
import { ChevronRight, CheckCircle2, Circle } from 'lucide-react'
import type { Instance } from '@/types'

async function fetchInstances(): Promise<Instance[]> {
  try { const r = await railsApi.get('/api/v1/instances'); if (!r.ok) return []; return r.json() }
  catch { return [] }
}

type Connector = {
  id: string
  name: string
  description: string
  logo: { light: string; dark?: string }
  href: string
  fields: (keyof Instance)[]
  available: boolean
}

const CONNECTORS: Connector[] = [
  {
    id: 'asana',
    name: 'Asana',
    description: 'Gerenciamento de tarefas, atas de reunião e consultas via WhatsApp.',
    logo: { light: 'https://svgl.app/library/asana-logo.svg' },
    href: '/settings/conectores/asana',
    fields: ['asana_access_token', 'asana_workspace_gid'],
    available: true,
  },
  {
    id: 'google-drive',
    name: 'Google Drive',
    description: 'Armazenamento e compartilhamento de arquivos da equipe.',
    logo: { light: 'https://svgl.app/library/drive.svg' },
    href: '/settings/conectores/google-drive',
    fields: [],
    available: true,
  },
]

export default async function ConectoresPage() {
  await requireAdmin()
  const instances = await fetchInstances()

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">Conectores</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
          Contas da equipe conectadas às instâncias e membros.
        </p>
      </div>

      <div className="flex flex-col gap-2">
        {CONNECTORS.map(connector => {
          const configured = connector.fields.length > 0
            ? instances.filter(i => connector.fields.every(f => !!i[f]))
            : []
          const total = instances.length

          return (
            <div key={connector.id} className={!connector.available ? 'opacity-50 cursor-not-allowed' : ''}>
              <Link
                href={connector.available ? connector.href : '#'}
                className={`group flex items-center justify-between p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 transition-all ${
                  connector.available
                    ? 'hover:border-zinc-300 dark:hover:border-zinc-600 hover:shadow-sm'
                    : 'pointer-events-none'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-white dark:bg-zinc-800 border border-zinc-100 dark:border-zinc-700 flex items-center justify-center shadow-sm">
                    <Image
                      src={connector.logo.light}
                      alt={connector.name}
                      width={24}
                      height={24}
                      className="w-6 h-6 object-contain"
                      unoptimized
                    />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-zinc-900 dark:text-white">{connector.name}</p>
                      {!connector.available && (
                        <span className="text-xs px-1.5 py-0.5 rounded-md bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-500 font-medium">
                          Em breve
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">{connector.description}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4 shrink-0">
                  {connector.available && total > 0 && connector.fields.length > 0 && (
                    <div className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
                      {configured.length === total
                        ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                        : <Circle className="w-3.5 h-3.5" />
                      }
                      {configured.length}/{total} instâncias
                    </div>
                  )}
                  {connector.available && (
                    <ChevronRight className="w-4 h-4 text-zinc-300 dark:text-zinc-600 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors" />
                  )}
                </div>
              </Link>
            </div>
          )
        })}
      </div>
    </div>
  )
}
