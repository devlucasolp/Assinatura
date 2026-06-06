'use server'

import { railsApi } from '@/lib/rails-api'
import { revalidatePath } from 'next/cache'

export type AllowlistEntry = {
  id:           number
  host_pattern: string
  note:         string | null
  created_at:   string
}

export async function fetchAllowlist(instanceId: string): Promise<AllowlistEntry[]> {
  try {
    const res = await railsApi.get(`/api/v1/instances/${instanceId}/sandbox_allowlist`)
    if (!res.ok) return []
    return (await res.json()) as AllowlistEntry[]
  } catch {
    return []
  }
}

export async function addAllowlist(instanceId: string, host_pattern: string, note?: string) {
  try {
    const res = await railsApi.post(
      `/api/v1/instances/${instanceId}/sandbox_allowlist`,
      { entry: { host_pattern, note } },
    )
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao adicionar host' }
    }
    revalidatePath(`/instances/${instanceId}`)
    return { entry: (await res.json()) as AllowlistEntry }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}

export async function removeAllowlist(instanceId: string, id: number) {
  try {
    const res = await railsApi.delete(`/api/v1/instances/${instanceId}/sandbox_allowlist/${id}`)
    if (!res.ok && res.status !== 204) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao remover host' }
    }
    revalidatePath(`/instances/${instanceId}`)
    return { success: true }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}
