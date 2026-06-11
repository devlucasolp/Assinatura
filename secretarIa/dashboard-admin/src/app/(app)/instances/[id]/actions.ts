'use server'

const botUrl = process.env.BOT_BACKEND_URL || 'http://127.0.0.1:8000'

export async function createAndGetQrCode(instanceId: string) {
  const createRes = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/create`, { method: 'POST', cache: 'no-store' })
  if (!createRes.ok) throw new Error(`Falha ao criar instância: ${await createRes.text()}`)
  
  const qrRes = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/qr`, { method: 'GET', cache: 'no-store' })
  if (!qrRes.ok) throw new Error(`Falha ao buscar QR Code: ${await qrRes.text()}`)
  
  return await qrRes.json()
}

export async function fetchEvolutionInstances() {
  try {
    const res = await fetch(`${botUrl}/api/evolution/instances`, { cache: 'no-store' })
    if (!res.ok) return []
    return await res.json()
  } catch { return [] }
}

export async function fetchEvolutionStatus(instanceId: string) {
  try {
    const res = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/status`, { cache: 'no-store' })
    if (!res.ok) return null
    return await res.json()
  } catch { return null }
}

export async function fetchEvolutionSettings(instanceId: string) {
  try {
    const res = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/settings`, { cache: 'no-store' })
    if (!res.ok) return null
    return await res.json()
  } catch { return null }
}

export async function updateEvolutionSettings(instanceId: string, settings: any) {
  const res = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  if (!res.ok) throw new Error(await res.text())
}

export async function updateEvolutionProfile(instanceId: string, profile: any) {
  const res = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  })
  if (!res.ok) throw new Error(await res.text())
}

export async function logoutEvolutionInstance(instanceId: string) {
  const res = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/logout`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
}

export async function restartEvolutionInstance(instanceId: string) {
  const res = await fetch(`${botUrl}/api/instances/${instanceId}/evolution/restart`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
}

export async function deleteEvolutionInstance(instanceId: string) {
  const res = await fetch(`${botUrl}/api/instances/${instanceId}/evolution`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text())
}
