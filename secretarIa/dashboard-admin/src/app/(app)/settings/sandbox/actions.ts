'use server'

import { railsApi } from '@/lib/rails-api'

export type SandboxRun = {
  id:              number
  instance_id:     string
  exit_code:       number
  duration_ms:     number
  memory_peak_mb:  number | null
  killed:          boolean
  kill_reason:     string | null
  origin:          string | null
  created_at:      string
}

export type SandboxRunFull = SandboxRun & {
  code:   string
  stdout: string
  stderr: string
}

export type RunsResponse = {
  total:  number
  limit:  number
  offset: number
  runs:   SandboxRun[]
}

type Filters = {
  instance_id?: string
  status?:      'success' | 'error' | 'killed'
  limit?:       number
  offset?:      number
}

export async function fetchRuns(filters: Filters = {}): Promise<RunsResponse> {
  const params: Record<string, string> = {}
  if (filters.instance_id) params.instance_id = filters.instance_id
  if (filters.status)      params.status      = filters.status
  if (filters.limit)       params.limit       = String(filters.limit)
  if (filters.offset)      params.offset      = String(filters.offset)

  try {
    const res = await railsApi.get('/api/v1/sandbox_runs', params)
    if (!res.ok) return { total: 0, limit: 50, offset: 0, runs: [] }
    return (await res.json()) as RunsResponse
  } catch {
    return { total: 0, limit: 50, offset: 0, runs: [] }
  }
}

export async function fetchRunFull(id: number): Promise<SandboxRunFull | null> {
  try {
    const res = await railsApi.get(`/api/v1/sandbox_runs/${id}`)
    if (!res.ok) return null
    return (await res.json()) as SandboxRunFull
  } catch {
    return null
  }
}
