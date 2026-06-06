const BACKEND = (process.env.BOT_BACKEND_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function headers(extra?: HeadersInit): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(process.env.BOT_API_KEY ? { 'x-api-key': process.env.BOT_API_KEY } : {}),
    ...(extra ?? {}),
  }
}

export const botApi = {
  get: (path: string, params?: Record<string, string>) => {
    const url = new URL(`${BACKEND}${path}`)
    if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
    return fetch(url.toString(), { headers: headers(), cache: 'no-store', signal: AbortSignal.timeout(1500) })
  },
  post: (path: string, body: unknown) =>
    fetch(`${BACKEND}${path}`, { method: 'POST', headers: headers(), body: JSON.stringify(body), signal: AbortSignal.timeout(1500) }),
  put: (path: string, body: unknown) =>
    fetch(`${BACKEND}${path}`, { method: 'PUT', headers: headers(), body: JSON.stringify(body), signal: AbortSignal.timeout(1500) }),
  delete: (path: string) =>
    fetch(`${BACKEND}${path}`, { method: 'DELETE', headers: headers(), signal: AbortSignal.timeout(1500) }),
}
