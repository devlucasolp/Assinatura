'use client'

import { createContext, useContext, useState } from 'react'

type ShellContextType = {
  isMobileSidebarOpen: boolean
  setMobileSidebarOpen: (v: boolean) => void
  isDesktopSidebarOpen: boolean
  setDesktopSidebarOpen: (v: boolean) => void
}

const ShellContext = createContext<ShellContextType | undefined>(undefined)

export function ShellProvider({ children }: { children: React.ReactNode }) {
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [isDesktopSidebarOpen, setDesktopSidebarOpen] = useState(true)

  return (
    <ShellContext.Provider value={{ isMobileSidebarOpen, setMobileSidebarOpen, isDesktopSidebarOpen, setDesktopSidebarOpen }}>
      {children}
    </ShellContext.Provider>
  )
}

export function useShell() {
  const ctx = useContext(ShellContext)
  if (!ctx) throw new Error('useShell must be inside ShellProvider')
  return ctx
}
