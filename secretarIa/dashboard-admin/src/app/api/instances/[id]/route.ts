import { NextRequest, NextResponse } from 'next/server'
import { railsApi } from '@/lib/rails-api'

type Params = { params: Promise<{ id: string }> }

export async function GET(_: NextRequest, { params }: Params) {
  const { id } = await params
  const res  = await railsApi.get(`/api/v1/instances/${id}`)
  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { id }   = await params
  const body = await req.json()
  const res  = await railsApi.put(`/api/v1/instances/${id}`, body)
  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}

export async function DELETE(_: NextRequest, { params }: Params) {
  const { id } = await params
  const res = await railsApi.delete(`/api/v1/instances/${id}`)
  if (res.status === 204) return new NextResponse(null, { status: 204 })
  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
