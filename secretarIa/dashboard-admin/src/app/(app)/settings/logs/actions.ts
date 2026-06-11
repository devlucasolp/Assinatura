'use server'

import { botApi } from '@/lib/bot-api'

export type LogEntry = {
  time:   string
  level:  string
  source: string
  msg:    string
}

export type LogsResponse = {
  total: number
  logs:  LogEntry[]
}



type Filters = {
  source?: string
  level?:  string
  tail?:   number
}

export async function fetchLogs(filters: Filters = {}): Promise<LogsResponse> {
  const params: Record<string, string> = {}
  if (filters.source) params.source = filters.source
  if (filters.level)  params.level  = filters.level
  params.tail = String(filters.tail ?? 100)

  try {
    const res = await botApi.get('/system/logs', params)
    if (!res.ok) return { total: 0, logs: [] }
    return (await res.json()) as LogsResponse
  } catch {
    return { total: 0, logs: [] }
  }
}
