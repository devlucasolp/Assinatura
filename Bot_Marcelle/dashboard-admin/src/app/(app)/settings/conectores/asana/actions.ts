'use server'

import { railsApi } from '@/lib/rails-api'
import { revalidatePath } from 'next/cache'

export type AsanaCreds = {
  asana_access_token:  string
  asana_workspace_gid: string
  asana_project_gid:   string
  asana_section_gid:   string
  asana_user_gid:      string
}

export async function updateInstanceAsana(id: string, creds: AsanaCreds) {
  try {
    // PATCH é o correto para updates parciais — manda só os campos do Asana
    const res = await railsApi.patch(`/api/v1/instances/${id}`, { instance: creds })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao salvar integração' }
    }
    revalidatePath('/settings/conectores/asana')
    return { success: true }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}
