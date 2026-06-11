'use server'

import { railsApi } from '@/lib/rails-api'
import { revalidatePath } from 'next/cache'

export type SkillCatalogItem = {
  id:                   string
  name:                 string
  description:          string
  category:             'core' | 'asana' | 'media'
  always_on:            boolean
  customized:           boolean
  default_name:         string
  default_description:  string
}

export async function fetchSkills(): Promise<SkillCatalogItem[]> {
  try {
    const res = await railsApi.get('/api/v1/skills')
    if (!res.ok) return []
    return (await res.json()) as SkillCatalogItem[]
  } catch {
    return []
  }
}

export async function updateSkill(id: string, patch: { name?: string; description?: string }) {
  try {
    const res = await railsApi.patch(`/api/v1/skills/${id}`, { skill: patch })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao atualizar skill' }
    }
    revalidatePath('/settings/skills')
    return { skill: (await res.json()) as SkillCatalogItem }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}

export async function resetSkill(id: string) {
  try {
    const res = await railsApi.delete(`/api/v1/skills/${id}`)
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao restaurar padrão' }
    }
    revalidatePath('/settings/skills')
    return { skill: (await res.json()) as SkillCatalogItem }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}
