'use client'

import Link from 'next/link'
import { Plus, Phone, MessageSquare, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import type { Instance } from '@/types'

function InstanceCard({ inst }: { inst: Instance }) {
  const initials = inst.name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()

  return (
    <Link
      href={`/instances/${inst.id}`}
      className="group flex items-start gap-5 p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-600 hover:shadow-sm transition-all"
    >
      {/* Avatar */}
      <div className="shrink-0 w-11 h-11 rounded-xl bg-violet-50 dark:bg-violet-950/50 border border-violet-100 dark:border-violet-900/50 flex items-center justify-center text-violet-700 dark:text-violet-400 font-semibold text-sm">
        {initials}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="font-semibold text-zinc-900 dark:text-white truncate">{inst.name}</p>
            <p className="text-xs text-zinc-400 dark:text-zinc-500 font-mono mt-0.5">{inst.id}</p>
          </div>
          <ArrowRight className="shrink-0 w-4 h-4 text-zinc-300 dark:text-zinc-600 group-hover:text-violet-500 group-hover:translate-x-0.5 transition-all mt-0.5" />
        </div>

        <div className="flex flex-wrap gap-x-5 gap-y-1 mt-3">
          <span className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
            <Phone className="w-3 h-3 shrink-0" />
            {inst.phone_primary}
          </span>
          {inst.evolution_instance && (
            <span className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
              <MessageSquare className="w-3 h-3 shrink-0" />
              {inst.evolution_instance}
            </span>
          )}
        </div>
      </div>
    </Link>
  )
}

export function InstancesClient({ initialInstances }: { initialInstances: Instance[] }) {
  if (initialInstances.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-14 h-14 rounded-2xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center mb-4">
          <MessageSquare className="w-6 h-6 text-zinc-400" />
        </div>
        <p className="font-medium text-zinc-900 dark:text-white mb-1">Nenhuma instância ainda</p>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-6">Crie a primeira para começar a configurar bots.</p>
        <Link href="/instances/new">
          <Button>
            <Plus className="w-4 h-4" />
            Criar instância
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {initialInstances.map(inst => (
        <InstanceCard key={inst.id} inst={inst} />
      ))}
    </div>
  )
}
