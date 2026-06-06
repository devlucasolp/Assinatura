import { NextResponse } from 'next/server'
import { requireAdmin } from '@/lib/auth'

/**
 * Redireciona o admin para o fluxo OAuth do Google Drive no Python (FastAPI),
 * injetando o secret server-side para nunca expor no bundle do cliente.
 */
export async function GET() {
  await requireAdmin()

  const backend = (process.env.BOT_BACKEND_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
  const secret  = process.env.OAUTH_SECRET ?? ''

  const url = new URL(`${backend}/auth/drive`)
  if (secret) url.searchParams.set('secret', secret)

  return NextResponse.redirect(url, { status: 302 })
}
