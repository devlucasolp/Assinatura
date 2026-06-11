import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { getSessionUser, SESSION_COOKIE } from '@/lib/auth'
import { ShellProvider } from '@/contexts/ShellContext'
import { ToastProvider } from '@/contexts/ToastContext'
import { Toaster } from '@/components/ui/Toaster'
import { Sidebar } from '@/components/Sidebar'
import { Shell } from '@/components/Shell'

async function logout() {
  'use server'
  const jar = await cookies()
  jar.delete(SESSION_COOKIE)
  redirect('/login')
}

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const user = await getSessionUser()

  if (!user) redirect('/login')

  return (
    <ShellProvider>
      <ToastProvider>
        <Sidebar role={user.role} onLogout={logout} />
        <Shell>{children}</Shell>
        <Toaster />
      </ToastProvider>
    </ShellProvider>
  )
}
