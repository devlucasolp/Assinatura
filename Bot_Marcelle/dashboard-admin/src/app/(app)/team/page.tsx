import { requireAdmin } from '@/lib/auth'

export default async function TeamPage() {
  await requireAdmin()

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">Equipe</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">Gestão de membros e permissões</p>
      </div>
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-8 text-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Em breve — gestão de equipe.</p>
      </div>
    </div>
  )
}
