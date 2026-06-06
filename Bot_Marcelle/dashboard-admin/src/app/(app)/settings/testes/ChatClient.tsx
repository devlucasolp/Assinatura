'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Send, Plug, PlugZap } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import type { Instance } from '@/types'

type Message = { role: 'user' | 'bot' | 'system'; text: string; ts: number }
type Props = { instances: Instance[]; wsBase: string }

export function ChatClient({ instances, wsBase }: Props) {
  const [instanceId, setInstanceId] = useState(instances[0]?.id ?? '')
  const [phone, setPhone] = useState('5511999990000')
  const [messages, setMessages] = useState<Message[]>([
    { role: 'system', text: 'Selecione uma instância e conecte para testar.', ts: Date.now() },
  ])
  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const [connecting, setConnecting] = useState(false)

  const wsRef = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (role: Message['role'], text: string) =>
    setMessages(prev => [...prev, { role, text, ts: Date.now() }])

  const connect = useCallback(() => {
    if (!instanceId || !phone.trim()) return
    setConnecting(true)
    addMessage('system', `Conectando à instância ${instanceId}...`)
    const ws = new WebSocket(`${wsBase}/teste/ws/${instanceId}/${phone.trim()}`)
    wsRef.current = ws
    ws.onopen = () => { setConnected(true); setConnecting(false); addMessage('system', 'Conectado!') }
    ws.onmessage = e => addMessage('bot', e.data)
    ws.onclose = () => { setConnected(false); setConnecting(false); wsRef.current = null; addMessage('system', 'Desconectado.') }
    ws.onerror = () => { addMessage('system', 'Erro na conexão WebSocket.'); setConnecting(false) }
  }, [instanceId, phone, wsBase])

  const disconnect = () => wsRef.current?.close()

  const send = () => {
    const text = input.trim()
    if (!text || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    addMessage('user', text)
    wsRef.current.send(text)
    setInput('')
  }

  const selectCls = 'rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-zinc-900 dark:text-zinc-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 disabled:opacity-50 transition-all'

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 overflow-hidden min-h-0">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3 px-4 py-3 border-b border-zinc-100 dark:border-zinc-800 shrink-0">
        <select value={instanceId} onChange={e => setInstanceId(e.target.value)} disabled={connected} className={`flex-1 min-w-0 ${selectCls}`}>
          {instances.length === 0 && <option value="">Nenhuma instância</option>}
          {instances.map(i => <option key={i.id} value={i.id}>{i.name} ({i.id})</option>)}
        </select>
        <input type="text" value={phone} onChange={e => setPhone(e.target.value)} disabled={connected} placeholder="Telefone fictício" className={`w-44 ${selectCls}`} />
        {connected
          ? <Button variant="ghost" size="sm" onClick={disconnect} className="text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"><PlugZap className="w-4 h-4" />Desconectar</Button>
          : <Button size="sm" onClick={connect} loading={connecting} disabled={!instanceId}><Plug className="w-4 h-4" />Conectar</Button>
        }
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-5 flex flex-col gap-3 min-h-0">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : m.role === 'system' ? 'justify-center' : 'justify-start'}`}>
            {m.role === 'system'
              ? <span className="text-xs text-zinc-400 dark:text-zinc-500 px-2">{m.text}</span>
              : <div className={`max-w-[72%] px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 rounded-br-sm'
                    : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-bl-sm'
                }`}>{m.text}</div>
            }
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex items-end gap-2 px-4 py-3 border-t border-zinc-100 dark:border-zinc-800 shrink-0">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
          disabled={!connected}
          placeholder={connected ? 'Digite uma mensagem… (Enter para enviar)' : 'Conecte primeiro'}
          rows={1}
          className="flex-1 resize-none rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-zinc-900 dark:text-zinc-100 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 disabled:opacity-40 placeholder:text-zinc-400 transition-all"
          style={{ maxHeight: '120px' }}
          onInput={e => { const el = e.currentTarget; el.style.height = 'auto'; el.style.height = `${Math.min(el.scrollHeight, 120)}px` }}
        />
        <Button size="sm" onClick={send} disabled={!connected || !input.trim()} className="shrink-0">
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}
