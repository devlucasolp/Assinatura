'use server'

import { railsApi } from '@/lib/rails-api'
import { revalidatePath } from 'next/cache'

type ConnectorTokenRow = {
  id: number
  connector: string
  instance_id: string
  scope: string | null
  updated_at: string
}

export async function checkGoogleDriveStatus() {
  try {
    const res = await railsApi.get('/api/v1/connector_tokens')
    if (!res.ok) return { isConnected: false }
    const tokens = (await res.json()) as ConnectorTokenRow[]
    const isConnected = tokens.some(t => t.connector === 'google_drive')
    return { isConnected }
  } catch {
    return { isConnected: false }
  }
}

export async function disconnectGoogleDrive() {
  try {
    const res = await railsApi.delete('/api/v1/connector_tokens/google_drive')
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { error: data.error ?? 'Erro ao desconectar' }
    }
    revalidatePath('/settings/conectores/google-drive')
    return { success: true }
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : 'Erro de rede' }
  }
}
