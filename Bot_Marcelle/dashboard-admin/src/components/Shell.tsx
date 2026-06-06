'use client'

import { Menu } from 'lucide-react'
import { useShell } from '@/contexts/ShellContext'

export function Shell({ children }: { children: React.ReactNode }) {
  const { setMobileSidebarOpen } = useShell()

  return (
    <div className="lg:pl-64 min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <header className="sticky top-0 z-30 flex items-center gap-4 px-6 py-4 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 lg:hidden">
        <button
          onClick={() => setMobileSidebarOpen(true)}
          className="p-2 -ml-2 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <span className="font-semibold text-zinc-900 dark:text-white text-sm">Assinatura Admin</span>
      </header>

      <main className="p-6 sm:p-8">
        {children}
      </main>
    </div>
  )
}
