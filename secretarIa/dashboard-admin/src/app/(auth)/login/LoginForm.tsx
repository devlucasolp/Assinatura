'use client'

import { useActionState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { loginAction } from './actions'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { PasswordInput } from '@/components/ui/PasswordInput'
import { Bot, Info } from 'lucide-react'

type State = { error?: string } | null

const OAUTH_ERRORS: Record<string, string> = {
  google_denied:  'Login com Google cancelado.',
  invalid_state:  'Sessão OAuth expirada. Tente novamente.',
  token_exchange: 'Erro ao autenticar com Google. Tente novamente.',
  not_allowed:    'Este e-mail não tem acesso ao painel.',
  missing_code:   'Resposta inválida do Google.',
  no_email:       'Não foi possível obter o e-mail da conta Google.',
}

function GoogleIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  )
}

export function LoginForm() {
  const [state, action, pending] = useActionState<State, FormData>(loginAction, null)
  const searchParams = useSearchParams()
  const oauthError = searchParams.get('error')

  const errorMessage = state?.error ?? (oauthError ? OAUTH_ERRORS[oauthError] : null)

  return (
    <div className="w-full max-w-sm">
      <div className="flex flex-col items-center gap-2 mb-8">
        <div className="w-12 h-12 rounded-2xl bg-violet-600 flex items-center justify-center">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-white">Assinatura Admin</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Entre para gerenciar os bots</p>
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 p-6 flex flex-col gap-4 shadow-sm">

        {/* Aviso de domínio */}
        <div className="flex items-start gap-2.5 px-3 py-2.5 rounded-lg bg-violet-50 dark:bg-violet-950/40 border border-violet-100 dark:border-violet-900/60">
          <Info className="w-4 h-4 text-violet-500 dark:text-violet-400 mt-0.5 shrink-0" />
          <p className="text-xs text-violet-700 dark:text-violet-300 leading-relaxed">
            Acesso restrito a e-mails{' '}
            <span className="font-semibold">@assinaturamarcapropria.com.br</span>.
          </p>
        </div>

        {errorMessage && (
          <div className="px-3 py-2 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-400">
            {errorMessage}
          </div>
        )}

        <a
          href="/api/auth/google"
          className="flex items-center justify-center gap-2.5 w-full px-4 py-2.5 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-sm font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-zinc-700/60 transition-colors"
        >
          <GoogleIcon />
          Entrar com Google
        </a>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-zinc-100 dark:bg-zinc-800" />
          <span className="text-xs text-zinc-400 dark:text-zinc-500">ou</span>
          <div className="flex-1 h-px bg-zinc-100 dark:bg-zinc-800" />
        </div>

        <form action={action} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">E-mail</label>
            <Input name="email" type="email" placeholder="voce@assinaturamarcapropria.com.br" required autoComplete="email" />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Senha</label>
            <PasswordInput name="password" placeholder="••••••••" required autoComplete="current-password" />
          </div>

          <Button type="submit" loading={pending} className="w-full">
            Entrar
          </Button>

          <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
            Não tem conta?{' '}
            <Link href="/register" className="text-violet-600 dark:text-violet-400 hover:underline font-medium">
              Criar conta
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
