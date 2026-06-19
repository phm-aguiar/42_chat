import { useEffect, useRef } from 'react'
import type { ChatMessage } from './ChatRoom'
import Avatar from './Avatar'
import UserSignature from './UserSignature'

interface MessageListProps {
  messages: ChatMessage[]
  currentUser: string
}

export default function MessageList({ messages, currentUser }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const prevCountRef = useRef(messages.length)

  // Auto-scroll para baixo em novas mensagens (se já estava no bottom)
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const wasAtBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight < 100

    if (wasAtBottom || messages.length > prevCountRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    prevCountRef.current = messages.length
  }, [messages])

  // Scroll infinito: carregar mais mensagens ao chegar no topo
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleScroll = () => {
      if (container.scrollTop === 0) {
        // TODO: carregar histórico mais antigo via REST (before param)
        // MVP: já carregou 50 na montagem, scroll infinito para features futuras
      }
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-2"
    >
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-600 text-sm uppercase tracking-widest">
            Nenhuma mensagem ainda. Seja o primeiro a falar!
          </p>
        </div>
      )}

      {messages.map((msg, i) => {
        const isSystem = msg.type === 'system'
        const isMine = msg.login === currentUser

        if (isSystem) {
          return (
            <div key={i} className="text-center py-1">
              <span className="text-gray-500 text-xs uppercase tracking-widest">
                {msg.content === 'join' && `→ ${msg.login} entrou`}
                {msg.content === 'leave' && `← ${msg.login} saiu`}
                {msg.content === 'shutdown' && '⚠ Servidor desligando...'}
              </span>
            </div>
          )
        }

        return (
          <div
            key={msg.id || i}
            className={`flex gap-3 py-2 ${isMine ? 'flex-row-reverse' : ''}`}
          >
            <Avatar login={msg.login || '?'} imageUrl={msg.image_url} />
            <div className={`flex-1 min-w-0 ${isMine ? 'text-right' : ''}`}>
              <div className="flex items-baseline gap-2 mb-1">
                <span className="text-xs font-bold uppercase text-lime">
                  {msg.login}
                </span>
                <span className="text-xs text-gray-600">
                  {msg.created_at
                    ? new Date(msg.created_at).toLocaleTimeString('pt-BR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                    : ''}
                </span>
              </div>
              <p className={`text-sm leading-relaxed break-words ${isMine ? 'text-white' : 'text-gray-200'}`}>
                {msg.content}
              </p>
              {msg.type === 'message' && msg.user_id != null && (
                <UserSignature userId={msg.user_id} />
              )}
            </div>
          </div>
        )
      })}

      <div ref={bottomRef} />
    </div>
  )
}
