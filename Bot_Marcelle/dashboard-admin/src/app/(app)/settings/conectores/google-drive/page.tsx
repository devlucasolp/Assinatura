import { requireAdmin } from '@/lib/auth'
import { checkGoogleDriveStatus } from './actions'
import { GoogleDriveClient } from './GoogleDriveClient'

export default async function GoogleDriveConnectorPage() {
  await requireAdmin()
  const { isConnected } = await checkGoogleDriveStatus()

  return <GoogleDriveClient initiallyConnected={isConnected} />
}
