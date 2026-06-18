import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET() {
  cookies()
  const clientId = process.env.GOOGLE_CLIENT_ID
  const redirectUri = 'http://127.0.0.1:3000/api/auth/google/callback'

  if (!clientId || !redirectUri) {
    return NextResponse.json(
      { error: 'GOOGLE_CLIENT_ID ou GOOGLE_OAUTH_REDIRECT_URI não configurados' },
      { status: 500 },
    )
  }

  const state = crypto.randomUUID()

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: 'openid email profile',
    access_type: 'offline',
    prompt: 'select_account',
    state,
  })

  const res = NextResponse.redirect(
    `https://accounts.google.com/o/oauth2/v2/auth?${params}`,
  )

  res.cookies.set('oauth_state', state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 10, // 10 min
    path: '/',
  })

  return res
}
