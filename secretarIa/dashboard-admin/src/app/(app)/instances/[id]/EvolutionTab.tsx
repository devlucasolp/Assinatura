'use client'

import { useState, useEffect } from 'react'
import { QrCode, LogOut, RefreshCw, Trash2, Smartphone, Battery, PhoneOff, EyeOff, CheckCheck, MessageCircleOff, UserCircle, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Toggle } from '@/components/ui/Toggle'
import { useToast } from '@/contexts/ToastContext'
import type { Instance } from '@/types'
import {
  createAndGetQrCode,
  fetchEvolutionInstances,
  fetchEvolutionStatus,
  fetchEvolutionSettings,
  updateEvolutionSettings,
  updateEvolutionProfile,
  logoutEvolutionInstance,
  restartEvolutionInstance,
  deleteEvolutionInstance
} from './actions'

export function EvolutionTab({ instance, onChange }: { instance: Instance; onChange: (k: keyof Instance, v: any) => void }) {
  const { toast } = useToast()
  
  const [statusData, setStatusData] = useState<any>(null)
  const [settings, setSettings] = useState<any>(null)
  const [profile, setProfile] = useState({ name: '', description: '' })
  
  const [qrModalOpen, setQrModalOpen] = useState(false)
  const [qrCodeBase64, setQrCodeBase64] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  const hasEvolution = !!instance.evolution_instance

  const [availableInstances, setAvailableInstances] = useState<any[]>([])

  const loadData = async () => {
    setFetching(true)
    try {
      const instancesList = await fetchEvolutionInstances()
      if (Array.isArray(instancesList)) {
        setAvailableInstances(instancesList)
        
        if (instance.evolution_instance) {
          const found = instancesList.find(i => (i?.name || i?.instance?.instanceName || i?.id) === instance.evolution_instance)
          if (found) {
            setStatusData({ instance: { state: found.connectionStatus || found.instance?.state, battery: found.battery || found.instance?.battery } })
            
            if (found.Setting) {
              setSettings({
                reject_call: found.Setting.rejectCall,
                always_online: found.Setting.alwaysOnline,
                read_messages: found.Setting.readMessages,
                groups_ignore: found.Setting.groupsIgnore,
                ...found.Setting
              })
            } else {
              setSettings(null)
            }

            setProfile({
              name: found.profileName || found.instance?.profileName || '',
              description: found.profileStatus || found.instance?.profileStatus || ''
            })

            // Atualiza também o telefone se estiver vazio na instância atual
            const jid = found.ownerJid || found.instance?.ownerJid || ''
            const jidNumber = jid.split('@')[0]
            const foundNumber = found.number || found.instance?.number || jidNumber
            
            console.log("EvolutionTab Sync -> found:", found)
            console.log("EvolutionTab Sync -> extracted number:", foundNumber, "current phone:", instance.phone_primary)
            
            if (foundNumber && !instance.phone_primary) {
              console.log("Updating phone_primary to", foundNumber)
              setTimeout(() => onChange('phone_primary', foundNumber), 0)
            }

            // Atualiza também o Nome interno do sistema na aba Geral, se estiver vazio
            const foundName = found.profileName || found.instance?.profileName || found.name || found.instance?.instanceName
            if (foundName && !instance.name) {
              console.log("Updating name to", foundName)
              setTimeout(() => onChange('name', foundName), 0)
            }

            setFetching(false)
            return
          }
        }
      }
    } catch {}

    if (!hasEvolution) {
      setStatusData(null)
      setSettings(null)
      setFetching(false)
      return
    }

    try {
      const st = await fetchEvolutionStatus(instance.id)
      setStatusData(st)
      const setts = await fetchEvolutionSettings(instance.id)
      if (setts) setSettings(setts)
    } catch {
      // Ignorar erros caso API esteja fora
    } finally {
      setFetching(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [instance.evolution_instance])

  const handleAction = async (action: 'logout' | 'restart' | 'delete', fn: () => Promise<void>) => {
    if (!confirm(`Tem certeza que deseja ${action} a instância na Evolution API?`)) return
    setLoading(true)
    try {
      await fn()
      toast(`Ação ${action} executada com sucesso.`, 'success')
      await loadData()
    } catch (e: any) {
      toast(`Erro: ${e.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async () => {
    if (!instance.evolution_instance) {
      toast('Defina um nome de instância Evolution primeiro.', 'error')
      return
    }
    setQrModalOpen(true)
    setLoading(true)
    setQrCodeBase64(null)
    try {
      const data = await createAndGetQrCode(instance.id)
      const base64 = data.base64 || data.qrcode?.base64
      if (base64) {
        setQrCodeBase64(base64.startsWith('data:image') ? base64 : `data:image/png;base64,${base64}`)
      } else {
        toast('QR Code não retornado. Instância já pode estar conectada.', 'error')
        setQrModalOpen(false)
      }
    } catch (e: any) {
      toast(e.message, 'error')
      setQrModalOpen(false)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveSettings = async () => {
    if (!settings) return
    setLoading(true)
    try {
      await updateEvolutionSettings(instance.id, settings)
      toast('Configurações salvas.', 'success')
    } catch (e: any) {
      toast(`Erro ao salvar: ${e.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveProfile = async () => {
    setLoading(true)
    try {
      await updateEvolutionProfile(instance.id, profile)
      toast('Perfil atualizado.', 'success')
    } catch (e: any) {
      toast(`Erro: ${e.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const stateStr = statusData?.instance?.state || 'Desconhecido'

  return (
    <div className="flex flex-col gap-10">
      
      {/* 1. Conexão Principal */}
      <section>
        <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Vínculo Evolution API</h3>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-6">Controle da ponte entre o painel e o WhatsApp.</p>
        
        <div className="grid grid-cols-2 gap-6">
          <div className="col-span-full md:col-span-1">
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
              Telefone Principal <span className="text-red-500">*</span>
            </label>
            <Input
              value={instance.phone_primary || ''}
              onChange={e => onChange('phone_primary', e.target.value)}
              placeholder="Ex: 5511999999999"
            />
          </div>

          <div className="col-span-full md:col-span-1">
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
              Telefone Secundário
            </label>
            <Input
              value={instance.phone_secondary || ''}
              onChange={e => onChange('phone_secondary', e.target.value)}
              placeholder="Ex: 5511988888888"
            />
          </div>

          <div className="col-span-full md:col-span-1">
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
              Nome da Instância na Evolution <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2">
              <Input
                value={instance.evolution_instance || ''}
                onChange={e => onChange('evolution_instance', e.target.value)}
                placeholder="Ex: gabi-bot"
                className="flex-1"
              />
              {availableInstances.length > 0 && (
                <select
                  className="w-48 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100"
                  onChange={e => {
                    if(e.target.value) onChange('evolution_instance', e.target.value)
                  }}
                  value=""
                >
                  <option value="">Buscar existente...</option>
                  {availableInstances.map((inst, i) => {
                    const val = inst?.name || inst?.instance?.instanceName || inst?.id || `instance-${i}`
                    return <option key={val} value={val}>{val}</option>
                  })}
                </select>
              )}
            </div>
            <p className="mt-1.5 text-xs text-zinc-500">Selecione uma existente ao lado ou digite para criar nova.</p>
          </div>

          <div className="col-span-full md:col-span-1">
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Status Atual</label>
            <div className="flex items-center gap-4 h-10 px-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-800">
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${stateStr === 'open' ? 'bg-green-500' : stateStr === 'connecting' ? 'bg-yellow-500 animate-pulse' : 'bg-zinc-400'}`} />
                <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300 capitalize">{stateStr}</span>
              </div>
              {statusData?.instance?.battery && (
                <div className="flex items-center gap-1.5 ml-auto text-zinc-500 text-xs">
                  <Battery className="w-3.5 h-3.5" />
                  {statusData.instance.battery}%
                </div>
              )}
            </div>
          </div>
        </div>

        {hasEvolution && (
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Button variant="primary" size="sm" onClick={handleConnect} disabled={loading} className="h-9">
              <QrCode className="w-4 h-4 mr-2" />
              Conectar (Gerar QR)
            </Button>
            <Button variant="secondary" size="sm" onClick={() => handleAction('restart', () => restartEvolutionInstance(instance.id))} disabled={loading} className="h-9">
              <RefreshCw className="w-4 h-4 mr-2" />
              Reiniciar Instância
            </Button>
            <Button variant="ghost" size="sm" onClick={() => handleAction('logout', () => logoutEvolutionInstance(instance.id))} disabled={loading} className="h-9 text-orange-600 hover:text-orange-700 hover:bg-orange-50">
              <LogOut className="w-4 h-4 mr-2" />
              Fazer Logout
            </Button>
            <Button variant="ghost" size="sm" onClick={() => handleAction('delete', () => deleteEvolutionInstance(instance.id))} disabled={loading} className="h-9 text-red-600 hover:text-red-700 hover:bg-red-50">
              <Trash2 className="w-4 h-4 mr-2" />
              Excluir na API
            </Button>
          </div>
        )}
      </section>

      {/* 2. Configurações Avançadas */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Comportamento do WhatsApp</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Regras e configurações nativas ativadas diretamente no aparelho.</p>
          </div>
          <Button size="sm" variant="secondary" onClick={handleSaveSettings} disabled={loading || !settings} className="h-8">
            Salvar Regras
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center gap-4 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
            <Toggle checked={settings?.reject_call || false} onChange={v => setSettings({ ...settings, reject_call: v })} />
            <div className="flex-1">
              <p className="text-sm font-semibold text-zinc-900 dark:text-white flex items-center gap-2"><PhoneOff className="w-4 h-4 text-zinc-400"/> Rejeitar Ligações</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">Recusa automaticamente voz/vídeo.</p>
            </div>
          </div>

          <div className="flex items-center gap-4 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
            <Toggle checked={settings?.always_online || false} onChange={v => setSettings({ ...settings, always_online: v })} />
            <div className="flex-1">
              <p className="text-sm font-semibold text-zinc-900 dark:text-white flex items-center gap-2"><Smartphone className="w-4 h-4 text-zinc-400"/> Sempre Online</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">Mantém o status online ativo.</p>
            </div>
          </div>

          <div className="flex items-center gap-4 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
            <Toggle checked={settings?.read_messages || false} onChange={v => setSettings({ ...settings, read_messages: v })} />
            <div className="flex-1">
              <p className="text-sm font-semibold text-zinc-900 dark:text-white flex items-center gap-2"><CheckCheck className="w-4 h-4 text-blue-400"/> Marcar como Lido</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">Ativa o tick azul automático.</p>
            </div>
          </div>

          <div className="flex items-center gap-4 px-4 py-3 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
            <Toggle checked={settings?.groups_ignore || false} onChange={v => setSettings({ ...settings, groups_ignore: v })} />
            <div className="flex-1">
              <p className="text-sm font-semibold text-zinc-900 dark:text-white flex items-center gap-2"><MessageCircleOff className="w-4 h-4 text-zinc-400"/> Ignorar Grupos</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">O bot ignora conversas em grupo.</p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Perfil */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-1">Perfil do WhatsApp</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Atualize os dados visíveis no perfil do bot.</p>
          </div>
          <Button size="sm" variant="secondary" onClick={handleSaveProfile} disabled={loading || !profile.name} className="h-8">
            Atualizar Perfil
          </Button>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Nome do Perfil</label>
            <Input value={profile.name} onChange={e => setProfile({ ...profile, name: e.target.value })} placeholder="Ex: Atendimento Bot" />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Recado (About)</label>
            <Input value={profile.description} onChange={e => setProfile({ ...profile, description: e.target.value })} placeholder="Ex: Atendimento 24h" />
          </div>
        </div>
      </section>

      {/* QR Modal */}
      {qrModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-zinc-900 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl border border-zinc-200 dark:border-zinc-800 animate-in fade-in zoom-in duration-200">
            <div className="p-4 border-b border-zinc-100 dark:border-zinc-800 flex justify-between items-center bg-zinc-50/50 dark:bg-zinc-900/50">
              <h3 className="font-semibold text-zinc-900 dark:text-white flex items-center gap-2">
                <QrCode className="w-4 h-4 text-violet-500" />
                Conectar WhatsApp
              </h3>
              <button onClick={() => setQrModalOpen(false)} className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 p-1 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-8 flex flex-col items-center justify-center min-h-[250px] text-center">
              {loading && !qrCodeBase64 ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
                  <p className="text-sm text-zinc-500">Configurando Evolution API e buscando QR Code...</p>
                </div>
              ) : qrCodeBase64 ? (
                <div className="flex flex-col items-center gap-4">
                  <div className="p-2 bg-white rounded-xl shadow-sm border border-zinc-200">
                    <img src={qrCodeBase64} alt="QR Code" className="w-48 h-48 object-contain" />
                  </div>
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">Abra o WhatsApp no celular e escaneie.</p>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
