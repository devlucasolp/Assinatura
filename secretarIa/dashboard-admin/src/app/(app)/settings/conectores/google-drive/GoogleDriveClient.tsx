'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowLeft, CheckCircle2, AlertCircle, Link as LinkIcon, Unlink } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/contexts/ToastContext'
import { disconnectGoogleDrive } from './actions'

const OAUTH_START_URL = '/api/connectors/google-drive/connect'

export function GoogleDriveClient({ initiallyConnected }: { initiallyConnected: boolean }) {
  const { toast } = useToast()
  const [isConnected, setIsConnected] = useState(initiallyConnected)
  const [loading, setLoading]         = useState(false)

  const handleConnect = () => {
    // OAuth real — redireciona para nossa rota proxy, que injeta o secret server-side
    // e encaminha para o Python (FastAPI) iniciar o fluxo Google.
    window.location.href = OAUTH_START_URL
  }

  const handleDisconnect = async () => {
    if (!confirm('Desconectar o Google Drive? Os bots não conseguirão mais fazer upload de arquivos.')) return

    setLoading(true)
    try {
      const res = await disconnectGoogleDrive()
      if (res.error) {
        toast(res.error, 'error')
      } else {
        setIsConnected(false)
        toast('Conta desconectada.', 'success')
      }
    } catch {
      toast('Erro inesperado ao desconectar.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center gap-3">
        <Link
          href="/settings/conectores"
          className="p-2 -ml-2 rounded-lg text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">Conector Google Drive</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">Gerencie a conexão da equipe com o Google Workspace</p>
        </div>
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <div className="p-8 border-b border-zinc-200 dark:border-zinc-800 flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center shadow-sm border border-zinc-100 mb-4">
            <Image
              src="https://svgl.app/library/drive.svg"
              alt="Google Drive"
              width={40}
              height={40}
              unoptimized
            />
          </div>
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">Google Drive</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 max-w-md mx-auto">
            Integre o Google Drive para permitir que os bots armazenem imagens, áudios, documentos e atas
            recebidos pelo WhatsApp.
          </p>

          <ul className="text-xs text-zinc-500 dark:text-zinc-400 mt-4 space-y-1 max-w-sm">
            <li>• Acesso restrito ao escopo <span className="font-mono">drive.file</span> (só arquivos criados pelo bot)</li>
            <li>• Token salvo no servidor — renovado automaticamente</li>
            <li>• Pastas: <span className="font-mono">Imagens/ Áudios/ Documentos/ Atas/</span></li>
          </ul>
        </div>

        <div className="p-8 bg-zinc-50 dark:bg-zinc-900/50">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 bg-white dark:bg-zinc-800 rounded-xl border border-zinc-200 dark:border-zinc-700/50">
            <div className="flex items-center gap-4">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${isConnected ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400'}`}>
                {isConnected ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
              </div>
              <div>
                <h3 className="font-medium text-zinc-900 dark:text-white">
                  {isConnected ? 'Conta conectada' : 'Não conectado'}
                </h3>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                  {isConnected ? 'Token ativo no servidor.' : 'Autorize uma conta Google para habilitar o upload.'}
                </p>
              </div>
            </div>

            <div className="shrink-0">
              {isConnected ? (
                <Button variant="danger" onClick={handleDisconnect} loading={loading}>
                  <Unlink className="w-4 h-4" />
                  Desconectar
                </Button>
              ) : (
                <Button onClick={handleConnect}>
                  <LinkIcon className="w-4 h-4" />
                  Conectar conta Google
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
