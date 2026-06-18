import { NextRequest, NextResponse } from 'next/server'
import { SESSION_COOKIE } from '@/lib/auth'
import { railsPost } from '@/lib/rails-api'

async function exchangeCode(code: string, redirectUri: string) {
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id:     process.env.GOOGLE_CLIENT_ID!,
      client_secret: process.env.GOOGLE_CLIENT_SECRET!,
      redirect_uri:  redirectUri,
      grant_type:    'authorization_code',
    }),
  })
  return res.json() as Promise<{ access_token?: string; error?: string }>
}

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl
  const code  = searchParams.get('code')
  const state = searchParams.get('state')
  const error = searchParams.get('error')

  const loginUrl = new URL('/login', 'http://127.0.0.1:3000')

  if (error) {
    loginUrl.searchParams.set('error', 'google_denied')
    return NextResponse.redirect(loginUrl)
  }

  const cookieState = req.cookies.get('oauth_state')?.value
  if (!state || !cookieState || state !== cookieState) {
    loginUrl.searchParams.set('error', 'invalid_state')
    loginUrl.searchParams.set('details', `s=${state}-c=${cookieState || 'missing'}`)
    return NextResponse.redirect(loginUrl)
  }

  if (!code) {
    loginUrl.searchParams.set('error', 'missing_code')
    return NextResponse.redirect(loginUrl)
  }

  const redirectUri = 'http://127.0.0.1:3000/api/auth/google/callback'

  const tokens = await exchangeCode(code, redirectUri)
  if (tokens.error || !tokens.access_token) {
    loginUrl.searchParams.set('error', 'token_exchange')
    loginUrl.searchParams.set('details', tokens.error || 'no_access_token')
    return NextResponse.redirect(loginUrl)
  }

  // Troca o token Google por um JWT do Rails
  let railsRes: Response
  try {
    railsRes = await railsPost('/api/v1/auth/sessions', { google_token: tokens.access_token })
  } catch (e: any) {
    loginUrl.searchParams.set('error', 'token_exchange')
    loginUrl.searchParams.set('details', 'rails_connection_failed')
    return NextResponse.redirect(loginUrl)
  }

  if (!railsRes.ok) {
    const key = railsRes.status === 403 ? 'not_allowed' : 'token_exchange'
    loginUrl.searchParams.set('error', key)
    return NextResponse.redirect(loginUrl)
  }

  const { token } = await railsRes.json()

  const res = NextResponse.redirect(new URL('/instances', 'http://127.0.0.1:3000'))
  res.cookies.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24,
    path: '/',
  })
  res.cookies.delete('oauth_state')

  return res
}
