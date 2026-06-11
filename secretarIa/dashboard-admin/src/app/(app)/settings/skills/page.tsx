import { requireAdmin } from '@/lib/auth'
import { Puzzle } from 'lucide-react'
import { fetchSkills } from './actions'
import { SkillsCatalogClient } from './SkillsCatalogClient'

export default async function SkillsPage() {
  await requireAdmin()
  const skills = await fetchSkills()

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-white flex items-center gap-2">
          <Puzzle className="w-5 h-5 text-violet-500" />
          Catálogo de Skills
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">
          Habilidades disponíveis no sistema. Renomeie ou personalize a descrição — o toggle por instância fica em cada bot.
        </p>
      </div>

      <SkillsCatalogClient initial={skills} />
    </div>
  )
}
