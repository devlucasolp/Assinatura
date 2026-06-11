import { cookies } from 'next/headers'
import { SESSION_COOKIE } from './auth'

const RAILS = (process.env.RAILS_API_URL || 'http://localhost:3000').replace(/\/$/, '')

async function authHeaders(extra?: HeadersInit): Promise<HeadersInit> {
  const jar = await cookies()
  const token = jar.get(SESSION_COOKIE)?.value
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(extra ?? {}),
  }
}

export const railsApi = {
  get: async (path: string, params?: Record<string, string>) => {
    const url = new URL(`${RAILS}${path}`)
    if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
    return fetch(url.toString(), { headers: await authHeaders(), cache: 'no-store', signal: AbortSignal.timeout(5000) })
  },
  post: async (path: string, body?: unknown) =>
    fetch(`${RAILS}${path}`, {
      method: 'POST',
      headers: await authHeaders(),
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(5000)
    }),
  put: async (path: string, body: unknown) =>
    fetch(`${RAILS}${path}`, { method: 'PUT', headers: await authHeaders(), body: JSON.stringify(body), signal: AbortSignal.timeout(5000) }),
  patch: async (path: string, body: unknown) =>
    fetch(`${RAILS}${path}`, { method: 'PATCH', headers: await authHeaders(), body: JSON.stringify(body), signal: AbortSignal.timeout(5000) }),
  delete: async (path: string) =>
    fetch(`${RAILS}${path}`, { method: 'DELETE', headers: await authHeaders(), signal: AbortSignal.timeout(5000) }),
}

/** Cliente sem auth — usado para login e OAuth callback. */
export async function railsPost(path: string, body: unknown) {
  return fetch(`${RAILS}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(5000)
  })
}
