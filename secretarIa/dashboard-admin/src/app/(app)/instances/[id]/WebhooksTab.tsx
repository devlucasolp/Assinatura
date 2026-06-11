import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/contexts/ToastContext'
import { Trash2, Copy } from 'lucide-react'

type Webhook = {
  id: number
  slug: string
  code: string
  enabled: boolean
}

export function WebhooksTab({ instanceId }: { instanceId: string }) {
  const { toast } = useToast()
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchWebhooks()
  }, [instanceId])

  const fetchWebhooks = async () => {
    try {
      const res = await fetch(`/api/instances/${instanceId}/webhooks`)
      if (!res.ok) throw new Error('Erro ao buscar webhooks')
      const data = await res.json()
      setWebhooks(data)
    } catch (e: any) {
      toast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Deseja deletar este webhook?')) return
    try {
      const res = await fetch(`/api/instances/${instanceId}/webhooks/${id}`, {
        method: 'DELETE'
      })
      if (!res.ok) throw new Error('Erro ao deletar')
      toast('Webhook deletado', 'success')
      fetchWebhooks()
    } catch (e: any) {
      toast(e.message, 'error')
    }
  }

  const copyUrl = (slug: string) => {
    const url = `${window.location.origin}/api/webhooks/${instanceId}/${slug}`
    navigator.clipboard.writeText(url)
    toast('URL copiada para a área de transferência', 'success')
  }

  if (loading) return <div className="p-4 text-zinc-500">Carregando...</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Webhooks</h2>
          <p className="text-sm text-zinc-500">Webhooks criados pela IA para receber requisições de outros sistemas.</p>
        </div>
      </div>

      {webhooks.length === 0 ? (
        <div className="p-8 text-center bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800">
          <p className="text-zinc-500 dark:text-zinc-400">Nenhum webhook encontrado.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {webhooks.map(webhook => (
            <div key={webhook.id} className="p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl flex items-start justify-between">
              <div className="space-y-2 w-full mr-4">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-zinc-900 dark:text-white">/{webhook.slug}</h3>
                  <Button variant="secondary" onClick={() => copyUrl(webhook.slug)} className="py-1 px-2 h-auto text-xs">
                    <Copy className="w-3 h-3 mr-1" /> Copiar URL
                  </Button>
                </div>
                <div className="p-3 bg-zinc-50 dark:bg-zinc-950 rounded-md border border-zinc-100 dark:border-zinc-800">
                  <pre className="text-xs font-mono text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap">
                    {webhook.code}
                  </pre>
                </div>
              </div>
              <Button variant="danger" onClick={() => handleDelete(webhook.id)} className="shrink-0 p-2 h-auto">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
