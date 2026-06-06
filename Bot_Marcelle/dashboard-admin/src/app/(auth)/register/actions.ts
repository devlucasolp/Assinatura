'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { SESSION_COOKIE } from '@/lib/auth'
import { railsPost } from '@/lib/rails-api'

type InvitePreview = { email: string; role: 'admin' | 'viewer'; expires_at: string }

/** Valida um invite_token e retorna seus dados — usado pelo SSR da página /register. */
export async function previewInvite(token: string): Promise<InvitePreview | null> {
  try {
    const res = await fetch(
      `${(process.env.RAILS_API_URL || 'http://localhost:3000').replace(/\/$/, '')}/api/v1/invites/${token}`,
      { cache: 'no-store' },
    )
    if (!res.ok) return null
    return (await res.json()) as InvitePreview
  } catch {
    return null
  }
}

export async function registerAction(_: unknown, formData: FormData) {
  const name         = formData.get('name') as string
  const email        = formData.get('email') as string
  const password     = formData.get('password') as string
  const confirm      = formData.get('confirm') as string
  const inviteToken  = (formData.get('invite_token') as string) || ''

  if (!name?.trim())            return { error: 'Nome é obrigatório.' }
  if (!email?.trim())           return { error: 'E-mail é obrigatório.' }
  if (!password)                return { error: 'Senha é obrigatória.' }
  if (password !== confirm)     return { error: 'As senhas não coincidem.' }
  if (password.length < 8)      return { error: 'A senha deve ter pelo menos 8 caracteres.' }

  let res: Response
  try {
    res = await railsPost('/api/v1/auth/register', {
      name,
      email,
      password,
      invite_token: inviteToken || undefined,
    })
  } catch {
    return { error: 'Não foi possível conectar ao servidor. Tente novamente.' }
  }

  if (res.status === 422) {
    const body = await res.json()
    return { error: body.error ?? 'Dados inválidos.' }
  }

  if (!res.ok) {
    return { error: 'Erro inesperado. Tente novamente.' }
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
