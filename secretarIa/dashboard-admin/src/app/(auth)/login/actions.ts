'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { SESSION_COOKIE } from '@/lib/auth'
import { railsPost } from '@/lib/rails-api'

export async function loginAction(_: unknown, formData: FormData) {
  const email    = formData.get('email') as string
  const password = formData.get('password') as string

  let res: Response
  try {
    res = await railsPost('/api/v1/auth/sessions', { email, password })
  } catch {
    return { error: 'Não foi possível conectar ao servidor. Tente novamente.' }
  }

  if (res.status === 401 || res.status === 403) {
    return { error: 'E-mail ou senha incorretos.' }
  }

  if (!res.ok) {
    let detail = ''
    try { const b = await res.json(); detail = b.error ?? JSON.stringify(b) } catch {}
    console.error('[LOGIN] Rails respondeu', res.status, detail)
    return { error: `Erro ${res.status}${detail ? `: ${detail}` : ''}` }
  }

  const { token } = await res.json()

  const jar = await cookies()
  jar.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24,
    path: '/',
  })

  redirect('/instances')
}
