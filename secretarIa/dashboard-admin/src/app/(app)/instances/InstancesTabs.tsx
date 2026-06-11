'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { InstancesClient } from './InstancesClient'
import { ChatClient } from './ChatClient'
import type { Instance } from '@/types'

type Tab = 'bots' | 'testes'

type Props = {
  instances: Instance[]
  wsBase: string
}

export function InstancesTabs({ instances, wsBase }: Props) {
  const [tab, setTab] = useState<Tab>('bots')

  const tabCls = (t: Tab) =>
    `px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
      tab === t
        ? 'border-zinc-900 dark:border-white text-zinc-900 dark:text-white'
        : 'border-transparent text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
    }`

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">Instâncias</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            {instances.length === 0
              ? 'Nenhum bot configurado.'
              : `${instances.length} bot${instances.length > 1 ? 's' : ''} configurado${instances.length > 1 ? 's' : ''}.`}
          </p>
        </div>
        {tab === 'bots' && instances.length > 0 && (
          <Link href="/instances/new">
            <Button size="sm"><Plus className="w-4 h-4" />Nova instância</Button>
          </Link>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-0.5 border-b border-zinc-200 dark:border-zinc-800 mb-6">
        <button className={tabCls('bots')}  onClick={() => setTab('bots')}>Bots</button>
        <button className={tabCls('testes')} onClick={() => setTab('testes')}>Testes</button>
      </div>

      {/* Content */}
      {tab === 'bots' && <InstancesClient initialInstances={instances} />}

      {tab === 'testes' && (
        <div className="flex flex-col" style={{ height: 'calc(100vh - 18rem)' }}>
          <ChatClient instances={instances} wsBase={wsBase} />
        </div>
      )}
    </div>
  )
}
