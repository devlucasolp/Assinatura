'use client'

import { useState } from 'react'
import { Plus, ShieldAlert } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/contexts/ToastContext'
import { updateUserRole, deleteUser } from './actions'
import { InviteModal } from './InviteModal'
import type { TeamMember } from './types'

type Props = {
  initialMembers: TeamMember[]
  currentUserId: string
}

function GoogleBadge() {
  return (
    <span
      title="Login via Google"
      className="inline-flex items-center text-[10px] font-medium px-1.5 py-0.5 rounded-md bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400"
    >
      Google
    </span>
  )
}

export function TeamClient({ initialMembers, currentUserId }: Props) {
  const { toast } = useToast()
  const [members, setMembers]       = useState<TeamMember[]>(initialMembers)
  const [processing, setProcessing] = useState<string | null>(null)
  const [inviteOpen, setInviteOpen] = useState(false)

  const handleRoleChange = async (id: string, newRole: TeamMember['role']) => {
    setProcessing(id)
    try {
      const res = await updateUserRole(id, newRole)
      if (res.error) {
        toast(res.error, 'error')
      } else {
        setMembers(members.map(m => m.id === id ? { ...m, role: newRole } : m))
        toast('Permissão atualizada.', 'success')
      }
    } catch {
      toast('Erro inesperado.', 'error')
    } finally {
      setProcessing(null)
    }
  }

  const handleRemove = async (id: string) => {
    if (!confirm('Remover este usuário?')) return

    setProcessing(id)
    try {
      const res = await deleteUser(id)
      if (res.error) {
        toast(res.error, 'error')
      } else {
        setMembers(members.filter(m => m.id !== id))
        toast('Usuário removido.', 'success')
      }
    } catch {
      toast('Erro inesperado.', 'error')
    } finally {
      setProcessing(null)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">Equipe e Permissões</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">Gestão de acesso e papéis de usuários.</p>
        </div>
        <Button size="sm" onClick={() => setInviteOpen(true)}>
          <Plus className="w-4 h-4" />
          Convidar Usuário
        </Button>
      </div>

      {inviteOpen && <InviteModal onClose={() => setInviteOpen(false)} />}

      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-zinc-50 dark:bg-zinc-800/50 text-zinc-500 dark:text-zinc-400">
              <tr>
                <th className="px-6 py-3 font-medium">Usuário</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Papel</th>
                <th className="px-6 py-3 font-medium text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {members.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-zinc-500">Nenhum membro encontrado.</td>
                </tr>
              )}
              {members.map(member => {
                const isSelf = member.id === currentUserId
                return (
                  <tr key={member.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-0.5">
                        <span className="font-medium text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
                          {member.name}
                          {isSelf && <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-md bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400">Você</span>}
                          {member.googleLinked && <GoogleBadge />}
                        </span>
                        <span className="text-zinc-500 text-xs">{member.email}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={member.active ? 'green' : 'yellow'}>
                        {member.active ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        disabled={processing === member.id || isSelf}
                        title={isSelf ? 'Você não pode alterar seu próprio papel' : undefined}
                        className="bg-transparent border border-zinc-300 dark:border-zinc-700 rounded p-1 text-zinc-700 dark:text-zinc-300 focus:ring-2 focus:ring-violet-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        value={member.role}
                        onChange={(e) => handleRoleChange(member.id, e.target.value as TeamMember['role'])}
                      >
                        <option value="admin">Administrador</option>
                        <option value="viewer">Visualizador</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemove(member.id)}
                        loading={processing === member.id}
                        disabled={isSelf}
                        title={isSelf ? 'Você não pode remover sua própria conta' : undefined}
                        className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/50 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent"
                      >
                        Remover
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 border border-blue-100 dark:border-blue-800/30">
        <ShieldAlert className="w-5 h-5 shrink-0" />
        <p className="text-sm">
          Apenas e-mails <span className="font-semibold">@assinaturamarcapropria.com.br</span> podem se registrar via <code className="font-mono text-xs">/register</code> ou login Google.
        </p>
      </div>
    </div>
  )
}
