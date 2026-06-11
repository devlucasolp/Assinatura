import { NextRequest, NextResponse } from 'next/server'
import { railsApi } from '@/lib/rails-api'

export async function GET() {
  const res = await railsApi.get('/api/v1/instances')
  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}

export async function POST(req: NextRequest) {
  const body = await req.json()
  const res  = await railsApi.post('/api/v1/instances', body)
  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
