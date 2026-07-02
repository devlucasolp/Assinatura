import { requireAuth } from '@/lib/auth'
import { railsApi } from '@/lib/rails-api'
import { InstanceEditor } from './InstanceEditor'
import type { Instance } from '@/types'
import { notFound } from 'next/navigation'

async function fetchInstance(id: string): Promise<Instance | null> {
  try {
    const res = await railsApi.get(`/api/v1/instances/${id}`)
    if (!res.ok) return null
    return res.json()
  } catch { return null }
}

type Props = { params: Promise<{ id: string }> }

export default async function InstanceDetailPage({ params }: Props) {
  await requireAuth()
  const { id } = await params
  const instance = await fetchInstance(id)

  if (!instance) notFound()

  return (
    <div className="max-w-4xl mx-auto">
      <InstanceEditor instance={instance} />
    </div>
  )
}
