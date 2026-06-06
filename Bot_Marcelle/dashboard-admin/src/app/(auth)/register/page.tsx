import { RegisterForm } from './RegisterForm'
import { previewInvite } from './actions'

type Props = { searchParams: Promise<{ token?: string }> }

export default async function RegisterPage({ searchParams }: Props) {
  const { token } = await searchParams
  const invite = token ? await previewInvite(token) : null

  return <RegisterForm invite={invite} inviteToken={token ?? ''} />
}
