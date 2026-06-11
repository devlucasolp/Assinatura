import { requireAuth } from '@/lib/auth'
import { InstanceEditor } from '../[id]/InstanceEditor'

export default async function NewInstancePage() {
  await requireAuth()

  return (
    <div className="max-w-4xl mx-auto">
      <InstanceEditor instance={null} />
    </div>
  )
}
