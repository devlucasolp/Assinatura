'use server'

import { railsApi } from '@/lib/rails-api'
import { revalidatePath } from 'next/cache'

export type InstanceSkill = {
  id:          string
  name:        string
  description: string
  category:    'core' | 'asana' | 'media'
  always_on:   boolean
  enabled:     boolean
}

type SkillsResponse = {
  instance_id: string
  skills:      InstanceSkill[]
}

export async function fetchInstanceSkills(instanceId: string): Promise<InstanceSkill[]> {
  try {
    const res = await railsApi.get(`/api/v1/instances/${instanceId}/skills`)
    if (!res.ok) return []
    const json = (await res.json()) as SkillsResponse
    return json.skills
  } catch {
    return []
  }
}

export async function updateInstanceSkills(instanceId: string, skills: Record<string, boolean>) {
  try {
    const res = await railsApi.put(`/api/v1/instances/${instanceId}/skills`, { skills })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao salvar skills' }
    }
    revalidatePath(`/instances/${instanceId}`)
    return { success: true }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}
