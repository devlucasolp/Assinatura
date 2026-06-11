import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/contexts/ToastContext'
import { Trash2 } from 'lucide-react'

type ScheduledTask = {
  id: number
  name: string
  cron_expression: string
  code: string
  enabled: boolean
}

export function ScheduledTasksTab({ instanceId }: { instanceId: string }) {
  const { toast } = useToast()
  const [tasks, setTasks] = useState<ScheduledTask[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTasks()
  }, [instanceId])

  const fetchTasks = async () => {
    try {
      const res = await fetch(`/api/instances/${instanceId}/scheduled_tasks`)
      if (!res.ok) throw new Error('Erro ao buscar tarefas')
      const data = await res.json()
      setTasks(data)
    } catch (e: any) {
      toast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Deseja deletar este agendamento?')) return
    try {
      const res = await fetch(`/api/instances/${instanceId}/scheduled_tasks/${id}`, {
        method: 'DELETE'
      })
      if (!res.ok) throw new Error('Erro ao deletar')
      toast('Agendamento deletado', 'success')
      fetchTasks()
    } catch (e: any) {
      toast(e.message, 'error')
    }
  }

  if (loading) return <div className="p-4 text-zinc-500">Carregando...</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Tarefas Agendadas (Cron)</h2>
          <p className="text-sm text-zinc-500">Agendamentos criados pela IA rodando na Sandbox.</p>
        </div>
      </div>

      {tasks.length === 0 ? (
        <div className="p-8 text-center bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800">
          <p className="text-zinc-500 dark:text-zinc-400">Nenhuma tarefa agendada encontrada.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map(task => (
            <div key={task.id} className="p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl flex items-start justify-between">
              <div className="space-y-1 w-full mr-4">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-zinc-900 dark:text-white">{task.name}</h3>
                  <span className="px-2 py-0.5 text-xs font-mono bg-zinc-100 dark:bg-zinc-800 rounded-md text-zinc-600 dark:text-zinc-400">
                    {task.cron_expression}
                  </span>
                </div>
                <div className="mt-2 p-3 bg-zinc-50 dark:bg-zinc-950 rounded-md border border-zinc-100 dark:border-zinc-800">
                  <pre className="text-xs font-mono text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap">
                    {task.code}
                  </pre>
                </div>
              </div>
              <Button variant="danger" onClick={() => handleDelete(task.id)} className="shrink-0 p-2 h-auto">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
