import { requireAdmin } from '@/lib/auth'
import Link from 'next/link'
import { Users, FileText, Plug, Puzzle, Box, ChevronRight } from 'lucide-react'

const items = [
  { href: '/settings/conectores', icon: Plug,     label: 'Conectores', description: 'Contas da equipe — Asana, Google Drive e outros serviços.' },
  { href: '/settings/skills',     icon: Puzzle,   label: 'Skills',     description: 'Habilidades disponíveis para os bots.' },
  { href: '/settings/sandbox',    icon: Box,      label: 'Sandbox',    description: 'Histórico de execuções de código Python pelos bots.' },
  { href: '/settings/team',       icon: Users,    label: 'Equipe',     description: 'Membros e permissões de acesso ao painel.' },
  { href: '/settings/logs',       icon: FileText, label: 'Logs',       description: 'Histórico de interações e auditoria dos bots.' },
]

export default async function SettingsPage() {
  await requireAdmin()

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">Configurações</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">Administração do sistema</p>
      </div>

      <div className="flex flex-col gap-2">
        {items.map(({ href, icon: Icon, label, description }) => (
          <Link
            key={href}
            href={href}
            className="group flex items-center justify-between px-5 py-4 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-600 hover:shadow-sm transition-all"
          >
            <div className="flex items-center gap-4">
              <div className="w-9 h-9 rounded-lg bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center text-zinc-500 dark:text-zinc-400 transition-colors">
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-900 dark:text-white">{label}</p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">{description}</p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-zinc-300 dark:text-zinc-600 group-hover:text-zinc-500 dark:group-hover:text-zinc-400 transition-colors" />
          </Link>
        ))}
      </div>
    </div>
  )
}
