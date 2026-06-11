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

  const loginUrl = new URL('/login', req.nextUrl.origin)

  if (error) {
    loginUrl.searchParams.set('error', 'google_denied')
    return NextResponse.redirect(loginUrl)
  }

  const cookieState = req.cookies.get('oauth_state')?.value
  if (!state || !cookieState || state !== cookieState) {
    loginUrl.searchParams.set('error', 'invalid_state')
    return NextResponse.redirect(loginUrl)
  }

  if (!code) {
    loginUrl.searchParams.set('error', 'missing_code')
    return NextResponse.redirect(loginUrl)
  }

  const redirectUri = process.env.GOOGLE_LOGIN_REDIRECT_URI ||
    `${req.nextUrl.origin}/api/auth/google/callback`

  const tokens = await exchangeCode(code, redirectUri)
  if (tokens.error || !tokens.access_token) {
    loginUrl.searchParams.set('error', 'token_exchange')
    return NextResponse.redirect(loginUrl)
  }

  // Troca o token Google por um JWT do Rails
  let railsRes: Response
  try {
    railsRes = await railsPost('/api/v1/auth/sessions', { google_token: tokens.access_token })
  } catch {
    loginUrl.searchParams.set('error', 'token_exchange')
    return NextResponse.redirect(loginUrl)
  }

  if (!railsRes.ok) {
    const key = railsRes.status === 403 ? 'not_allowed' : 'token_exchange'
    loginUrl.searchParams.set('error', key)
    return NextResponse.redirect(loginUrl)
  }

  const { token } = await railsRes.json()

  const res = NextResponse.redirect(new URL('/instances', req.nextUrl.origin))
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
