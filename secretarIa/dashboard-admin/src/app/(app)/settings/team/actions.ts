'use server'

import { railsApi } from '@/lib/rails-api'
import { revalidatePath } from 'next/cache'
import type { TeamMember } from './types'

type RailsUser = {
  id: number
  name: string
  email: string
  role: 'admin' | 'viewer'
  active: boolean
  google_sub: boolean
}

export async function fetchUsers(): Promise<TeamMember[]> {
  try {
    const res = await railsApi.get('/api/v1/users')
    if (!res.ok) return []
    const json = (await res.json()) as RailsUser[]
    return json.map(u => ({
      id:           String(u.id),
      name:         u.name,
      email:        u.email,
      role:         u.role,
      active:       u.active,
      googleLinked: u.google_sub,
    }))
  } catch {
    return []
  }
}

export async function updateUserRole(id: string, role: 'admin' | 'viewer') {
  try {
    const res = await railsApi.patch(`/api/v1/users/${id}`, { user: { role } })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao atualizar permissão' }
    }
    revalidatePath('/settings/team')
    return { success: true }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}

export type Invite = {
  id:         number
  token:      string
  email:      string
  role:       'admin' | 'viewer'
  invited_by: string
  expires_at: string
  created_at: string
}

export async function createInvite(email: string, role: 'admin' | 'viewer') {
  try {
    const res = await railsApi.post('/api/v1/invites', { invite: { email, role } })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao criar convite' }
    }
    const invite = (await res.json()) as Invite
    return { invite }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}

export async function deleteUser(id: string) {
  try {
    const res = await railsApi.delete(`/api/v1/users/${id}`)
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao remover usuário' }
    }
    revalidatePath('/settings/team')
    return { success: true }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}
