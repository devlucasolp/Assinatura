import { requireAuth } from '@/lib/auth'
import { api } from '@/lib/api'
import { InstanceEditor } from './InstanceEditor'
import type { Instance } from '@/types'
import { notFound } from 'next/navigation'

async function fetchInstance(id: string): Promise<Instance | null> {
  try {
    const res = await api.get(`/api/instances/${id}`)
    if (!res.ok) return null
    return res.json()
  } catch { return null }
}

type Props = { params: Promise<{ id: string }> }

export default async function InstanceDetailPage({ params }: Props) {
  await requireAuth()
  const { id } = await params
  let instance = await fetchInstance(id)
  
  if (!instance) {
    // Fallback Mock para quando a API não estiver rodando
    instance = {
      id,
      name: id.replace('-', ' ').toUpperCase(),
      phone_primary: '5511999999999',
      evolution_instance: `evolution-${id}`
    } as Instance
  }

  return (
    <div className="max-w-4xl mx-auto">
      <InstanceEditor instance={instance} />
    </div>
  )
}
