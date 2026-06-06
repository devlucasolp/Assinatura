'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Bot, Settings, Users, FileText, Plug, ChevronDown, X, Moon, Sun, LogOut, Puzzle, Sliders, Box } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useShell } from '@/contexts/ShellContext'
import type { UserRole } from '@/types'

type NavLeaf  = { kind?: 'leaf'; label: string; href: string; icon: React.ElementType; roles?: UserRole[] }
type NavGroup = { kind: 'group'; label: string; icon: React.ElementType; roles?: UserRole[]; children: NavLeaf[] }
type NavItem  = NavLeaf | NavGroup

const NAV: NavItem[] = [
  { label: 'Instâncias', href: '/instances', icon: Bot },
  {
    kind: 'group',
    label: 'Configurações',
    icon: Settings,
    roles: ['admin'],
    children: [
      { label: 'Conectores',   href: '/settings/conectores',   icon: Plug },
      { label: 'Skills',       href: '/settings/skills',       icon: Puzzle },
      { label: 'Sandbox',      href: '/settings/sandbox',      icon: Box },
      { label: 'Equipe',       href: '/settings/team',         icon: Users },
      { label: 'Logs',         href: '/settings/logs',         icon: FileText },
    ],
  },
]

const canAccess = (item: NavItem, role: UserRole) => !item.roles || item.roles.includes(role)

const itemCls = (active: boolean) =>
  `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
    active
      ? 'bg-violet-50 text-violet-700 dark:bg-violet-900/20 dark:text-violet-400'
      : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-200'
  }`

export function Sidebar({ role, onLogout }: { role: UserRole; onLogout: () => Promise<void> }) {
  const pathname = usePathname()
  const { isMobileSidebarOpen, setMobileSidebarOpen } = useShell()
  const [isDark, setIsDark] = useState(false)

  const defaultOpen = NAV.find(
    i => i.kind === 'group' && (i as NavGroup).children.some(c => pathname.startsWith(c.href))
  )
  const [openGroup, setOpenGroup] = useState<string | null>(defaultOpen?.label ?? null)

  useEffect(() => {
    const stored = localStorage.getItem('theme')
    const dark = stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches)
    setIsDark(dark)
    document.documentElement.classList.toggle('dark', dark)
  }, [])

  const toggleTheme = () => {
    const next = !isDark
    setIsDark(next)
    document.documentElement.classList.toggle('dark', next)
    localStorage.setItem('theme', next ? 'dark' : 'light')
  }

  return (
    <>
      {isMobileSidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setMobileSidebarOpen(false)} />
      )}

      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 flex flex-col
        bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800
        transition-transform duration-300
        ${isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0
      `}>
        {/* Brand */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center gap-2">
            <LayoutDashboard className="w-5 h-5 text-violet-600 dark:text-violet-400" />
            <span className="font-semibold text-zinc-900 dark:text-white text-sm">Assinatura Admin</span>
          </div>
          <button onClick={() => setMobileSidebarOpen(false)} className="lg:hidden p-1 rounded-md text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {NAV.filter(i => canAccess(i, role)).map(item => {
            if (item.kind === 'group') {
              const group = item as NavGroup
              const groupActive = group.children.some(c => pathname.startsWith(c.href))
              const expanded = openGroup === group.label
              const Icon = group.icon
              return (
                <div key={group.label}>
                  <button
                    onClick={() => setOpenGroup(prev => prev === group.label ? null : group.label)}
                    className={`${itemCls(groupActive)} w-full justify-between`}
                  >
                    <span className="flex items-center gap-3">
                      <Icon className="w-4 h-4 shrink-0" />
                      {group.label}
                    </span>
                    <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`} />
                  </button>
                  <div className={`overflow-hidden transition-all duration-200 ${expanded ? 'max-h-40 mt-1' : 'max-h-0'}`}>
                    {group.children.filter(c => canAccess(c, role)).map(({ label, href, icon: ChildIcon }) => (
                      <Link
                        key={href}
                        href={href}
                        onClick={() => setMobileSidebarOpen(false)}
                        className={`${itemCls(pathname === href || pathname.startsWith(href + '/'))} pl-11`}
                      >
                        <ChildIcon className="w-3.5 h-3.5 shrink-0" />
                        {label}
                      </Link>
                    ))}
                  </div>
                </div>
              )
            }

            const leaf = item as NavLeaf
            const Icon = leaf.icon
            const active = pathname === leaf.href || pathname.startsWith(leaf.href + '/')
            return (
              <Link key={leaf.href} href={leaf.href} onClick={() => setMobileSidebarOpen(false)} className={itemCls(active)}>
                <Icon className="w-4 h-4 shrink-0" />
                {leaf.label}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 space-y-1">
          <button onClick={toggleTheme} className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors">
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            {isDark ? 'Modo claro' : 'Modo escuro'}
          </button>
          <form action={onLogout}>
            <button className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 transition-colors">
              <LogOut className="w-4 h-4" />
              Sair
            </button>
          </form>
        </div>
      </aside>
    </>
  )
}
