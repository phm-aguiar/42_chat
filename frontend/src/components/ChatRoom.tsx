import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/auth'
import { useWebSocket } from '../lib/ws'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

export interface ChatMessage {
  id?: string
  type: 'message' | 'system'
  user_id?: number
  login?: string
  image_url?: string
  content?: string
  created_at?: string
}

export default function ChatRoom() {
  const navigate = useNavigate()
  const { token, user, isAuthenticated, logout } = useAuthStore()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [connected, setConnected] = useState(false)
  const [reconnecting, setReconnecting] = useState(false)
  const [onlineCount, setOnlineCount] = useState(0)

  const handleMessage = useCallback((msg: ChatMessage) => {
    setMessages(prev => {
      // Evitar duplicatas por ID
      if (msg.id && prev.some(m => m.id === msg.id)) return prev
      return [...prev, msg]
    })

    if (msg.type === 'system') {
      if (msg.content === 'join') setOnlineCount(c => c + 1)
      if (msg.content === 'leave') setOnlineCount(c => Math.max(0, c - 1))
    }
  }, [])

  const { send, close } = useWebSocket(
    handleMessage,
    () => {
      setConnected(true)
      setReconnecting(false)
    },
    () => {
      setConnected(false)
      setReconnecting(true)
    },
  )

  // Redirecionar se não autenticado
  useEffect(() => {
    if (!isAuthenticated || !token) {
      navigate('/')
    }
  }, [isAuthenticated, token, navigate])

  // Carregar histórico de mensagens
  useEffect(() => {
    if (!token) return
    fetch('/api/messages?limit=50', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setMessages(prev => {
            const existingIds = new Set(prev.map(m => m.id))
            const newMsgs = data
              .filter((m: ChatMessage) => !existingIds.has(m.id))
              .map((m: ChatMessage) => ({ ...m, type: 'message' as const }))
              .reverse() // API retorna DESC, exibimos ASC
            return [...newMsgs, ...prev]
          })
        }
      })
      .catch(err => console.error('Failed to load messages:', err))
  }, [token])

  const handleLogout = () => {
    close()
    logout()
    navigate('/')
  }

  const handleSend = (content: string) => {
    if (!content.trim()) return
    send(content)
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-black flex flex-col">
      {/* Header / Status Bar */}
      <header className="status-bar">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-black tracking-tighter">
            42<span className="text-lime">_</span>CHAT
          </h1>
          <span className="text-gray-500 text-xs">general</span>
        </div>

        <div className="flex items-center gap-4">
          {/* Connection status */}
          <div className="flex items-center gap-2 text-xs">
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-lime' : reconnecting ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-gray-400 uppercase">
              {connected ? `${onlineCount} online` : reconnecting ? 'reconectando...' : 'offline'}
            </span>
          </div>

          {/* User info + logout */}
          <div className="flex items-center gap-2">
            <div className="avatar-42" title={user.login}>
              {user.image_url ? (
                <img
                  src={user.image_url}
                  alt={user.login}
                  className="w-full h-full object-cover"
                />
              ) : (
                user.login.slice(0, 2).toUpperCase()
              )}
            </div>
            <span className="text-white text-xs font-bold uppercase">
              {user.login}
            </span>
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-magenta text-xs uppercase ml-2 cursor-pointer transition-colors"
            >
              Sair
            </button>
          </div>
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 flex flex-col dot-grid overflow-hidden">
        <MessageList messages={messages} currentUser={user.login} />
        <MessageInput onSend={handleSend} disabled={!connected} />
      </div>
    </div>
  )
}
