export type TeamMember = {
  id: string
  name: string
  email: string
  role: 'admin' | 'viewer'
  active: boolean
  googleLinked: boolean
}
