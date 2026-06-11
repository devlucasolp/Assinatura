import { requireAdmin } from '@/lib/auth'
import { fetchUsers } from './actions'
import { TeamClient } from './TeamClient'

export default async function TeamPage() {
  const me    = await requireAdmin()
  const users = await fetchUsers()

  return <TeamClient initialMembers={users} currentUserId={String(me.id)} />
}
