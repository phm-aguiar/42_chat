import { useAuthStore } from '../stores/auth'

export type MessageHandler = (msg: MessageFromServer) => void

export interface MessageFromServer {
  type: 'message' | 'system' | 'user_stats_changed'
  id?: string
  user_id?: number
  login?: string
  image_url?: string
  content?: string
  created_at?: string
  // user_stats_changed payload
  total_messages?: number
  active_rooms?: number
  tier?: string
}

interface UseWebSocketReturn {
  send: (content: string) => void
  close: () => void
  readyState: number
}

export function useWebSocket(
  onMessage: MessageHandler,
  onOpen?: () => void,
  onClose?: () => void,
): UseWebSocketReturn {
  const token = useAuthStore.getState().token

  if (!token) {
    return { ...noopWS, readyState: WebSocket.CLOSED }
  }

  // Singleton pattern via module-level (simplificado para MVP: 1 conexão)
  return getOrCreateWS(token, onMessage, onOpen, onClose)
}

// ---- Internal WebSocket manager ----

let ws: WebSocket | null = null
let connecting = false
const handlers: Set<MessageHandler> = new Set()
const openHandlers: Set<() => void> = new Set()
const closeHandlers: Set<() => void> = new Set()
let reconnectAttempts = 0
const MAX_RECONNECT_DELAY = 30000 // 30s max

function getOrCreateWS(
  token: string,
  onMessage: MessageHandler,
  onOpen?: () => void,
  onClose?: () => void,
): UseWebSocketReturn {
  handlers.add(onMessage)
  if (onOpen) openHandlers.add(onOpen)
  if (onClose) closeHandlers.add(onClose)

  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return {
      send: (content: string) => sendMessage(content),
      close: () => cleanupWS(),
      readyState: ws!.readyState,
    }
  }

  if (connecting) {
    return {
      send: (content: string) => sendMessage(content),
      close: () => cleanupWS(),
      readyState: WebSocket.CONNECTING,
    }
  }

  connect(token)
  return {
    send: (content: string) => sendMessage(content),
    close: () => cleanupWS(),
    readyState: ws?.readyState ?? WebSocket.CONNECTING,
  }
}

function connect(token: string) {
  if (connecting) return
  connecting = true

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.host
  const url = `${protocol}://${host}/ws?token=${encodeURIComponent(token)}`

  ws = new WebSocket(url)

  ws.onopen = () => {
    console.log('[WS] conectado')
    connecting = false
    reconnectAttempts = 0
    openHandlers.forEach(h => h())
  }

  ws.onmessage = (event) => {
    try {
      const msg: MessageFromServer = JSON.parse(event.data)
      handlers.forEach(h => h(msg))
    } catch (err) {
      console.error('[WS] parse error:', err)
    }
  }

  ws.onclose = (event) => {
    console.log('[WS] desconectado:', event.code, event.reason)
    connecting = false
    closeHandlers.forEach(h => h())

    // Reconexão com backoff exponencial
    if (event.code !== 1000 && event.code !== 1001) {
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), MAX_RECONNECT_DELAY)
      reconnectAttempts++
      console.log(`[WS] reconectando em ${delay}ms (tentativa ${reconnectAttempts})`)
      setTimeout(() => connect(token), delay)
    }
  }

  ws.onerror = (err) => {
    console.error('[WS] error:', err)
  }
}

function sendMessage(content: string) {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'message', content }))
  }
}

function cleanupWS() {
  connecting = false
  if (ws) {
    ws.close(1000, 'user logout')
    ws = null
  }
  handlers.clear()
  openHandlers.clear()
  closeHandlers.clear()
  reconnectAttempts = 0
}

const noopWS: UseWebSocketReturn = {
  send: () => {},
  close: () => {},
  readyState: WebSocket.CLOSED,
}
