'use server'

import { railsApi } from '@/lib/rails-api'
import { revalidatePath } from 'next/cache'

export type CustomSkill = {
  id:                number
  name:              string
  keywords:          string[]
  match_whole_word:  boolean
  response_template: string
  enabled:           boolean
  updated_at:        string
}

export type CustomSkillInput = {
  name:              string
  keywords:          string[]
  match_whole_word:  boolean
  response_template: string
  enabled:           boolean
}

export async function fetchCustomSkills(instanceId: string): Promise<CustomSkill[]> {
  try {
    const res = await railsApi.get(`/api/v1/instances/${instanceId}/custom_skills`)
    if (!res.ok) return []
    return (await res.json()) as CustomSkill[]
  } catch {
    return []
  }
}

export async function createCustomSkill(instanceId: string, input: CustomSkillInput) {
  try {
    const res = await railsApi.post(`/api/v1/instances/${instanceId}/custom_skills`, { custom_skill: input })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao criar skill' }
    }
    revalidatePath(`/instances/${instanceId}`)
    return { skill: (await res.json()) as CustomSkill }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}

export async function updateCustomSkill(instanceId: string, id: number, input: Partial<CustomSkillInput>) {
  try {
    const res = await railsApi.patch(`/api/v1/instances/${instanceId}/custom_skills/${id}`, { custom_skill: input })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao atualizar skill' }
    }
    revalidatePath(`/instances/${instanceId}`)
    return { skill: (await res.json()) as CustomSkill }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}

export async function deleteCustomSkill(instanceId: string, id: number) {
  try {
    const res = await railsApi.delete(`/api/v1/instances/${instanceId}/custom_skills/${id}`)
    if (!res.ok && res.status !== 204) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao remover skill' }
    }
    revalidatePath(`/instances/${instanceId}`)
    return { success: true }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}
