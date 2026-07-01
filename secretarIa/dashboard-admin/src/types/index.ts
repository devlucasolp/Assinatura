export type UserRole = 'admin' | 'viewer'

export type User = {
  id: number
  name: string
  email: string
  role: UserRole
}

export type Instance = {
  id: string
  name: string
  phone_primary: string
  phone_secondary?: string
  evolution_instance: string
  asana_access_token?: string
  asana_workspace_gid?: string
  asana_project_gid?: string
  asana_section_gid?: string
  asana_user_gid?: string
  gemini_api_key?: string
  msg_auto_reply_meeting?: string
  msg_auto_reply_event?: string
  msg_status_meeting_on?: string
  msg_status_event_on?: string
  msg_status_off?: string
  msg_greeting?: string
  assistant_name?: string
  system_prompt?: string
  briefing_morning?: string | null
  briefing_afternoon?: string | null
  briefing_evening?: string | null
  new_tasks_poll_minutes?: number | null
  briefing_timezone?: string
}

export type InstanceFormData = Omit<Instance, 'id'> & { id?: string }

export type ApiResponse<T> = {
  data: T
  error?: never
} | {
  data?: never
  error: string
}
