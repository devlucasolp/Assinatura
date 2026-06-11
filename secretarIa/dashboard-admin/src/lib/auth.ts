import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import type { User, UserRole } from '@/types'

export const SESSION_COOKIE = 'admin_session'

function parseJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const part = token.split('.')[1]
    if (!part) return null
    const json = Buffer.from(part, 'base64url').toString('utf-8')
    return JSON.parse(json)
  } catch {
    return null
  }
}

export async function getSessionUser(): Promise<User | null> {
  const jar = await cookies()
  const token = jar.get(SESSION_COOKIE)?.value
  if (!token) return null

  const payload = parseJwtPayload(token)
  if (!payload) return null

  const exp = payload['exp']
  if (typeof exp === 'number' && exp < Date.now() / 1000) return null

  const id    = payload['user_id']
  const name  = payload['name']
  const email = payload['email']
  const role  = payload['role']

  if (!id || !email || !role) return null

  return {
    id:    typeof id === 'number' ? id : Number(id),
    name:  typeof name === 'string' ? name : String(email),
    email: String(email),
    role:  String(role) as UserRole,
  }
}

export async function requireAuth(): Promise<User> {
  const user = await getSessionUser()
  if (!user) redirect('/login')
  return user
}

export async function requireAdmin(): Promise<User> {
  const user = await requireAuth()
  if (user.role !== 'admin') redirect('/instances')
  return user
}

export { SESSION_COOKIE as default }
