import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuthStore } from '../stores/auth'
import { useWebSocket, type MessageFromServer } from '../lib/ws'

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface UserStats {
  user_id: number
  login: string
  avatar_url: string
  total_messages: number
  active_rooms: number
  tier: 'novato' | 'iniciante' | 'participante' | 'veterano'
  member_since: string
}

interface UserSignatureProps {
  userId: number
}

// ---------------------------------------------------------------------------
// Configuração visual por tier
// ---------------------------------------------------------------------------

interface TierVisual {
  label: string
  icon: string
  color: string
  bg: string
  border: string
}

const TIER_MAP: Record<UserStats['tier'], TierVisual> = {
  novato: {
    label: 'Novato',
    icon: '🌱',
    color: 'text-gray-500',
    bg: 'bg-gray-950',
    border: 'border-gray-700',
  },
  iniciante: {
    label: 'Iniciante',
    icon: '🔰',
    color: 'text-cyan',
    bg: 'bg-cyan-950/50',
    border: 'border-cyan-800',
  },
  participante: {
    label: 'Participante',
    icon: '⭐',
    color: 'text-blue',
    bg: 'bg-blue-950/50',
    border: 'border-blue-800',
  },
  veterano: {
    label: 'Veterano',
    icon: '👑',
    color: 'text-lime',
    bg: 'bg-lime-950/50',
    border: 'border-lime-800',
  },
}

// ---------------------------------------------------------------------------
// Helper: iniciais para avatar placeholder
// ---------------------------------------------------------------------------

function initials(login: string): string {
  return login.slice(0, 2).toUpperCase()
}

// ---------------------------------------------------------------------------
// Componente
// ---------------------------------------------------------------------------

export default function UserSignature({ userId }: UserSignatureProps) {
  const token = useAuthStore((s) => s.token)

  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  // Ref estável para acessar userId dentro do callback do WebSocket
  const userIdRef = useRef(userId)
  userIdRef.current = userId

  // ---- Fetch stats via REST ------------------------------------------------

  useEffect(() => {
    let cancelled = false

    async function load() {
      if (!token) return

      setLoading(true)
      setError(null)

      try {
        const res = await fetch(`/api/users/${userId}/stats`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }

        const data: UserStats = await res.json()
        if (!cancelled) {
          setStats(data)
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Erro ao carregar stats')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [userId, token, refreshKey])

  // ---- WebSocket listener para atualização em tempo real -------------------

  const handleWSMessage = useCallback((msg: MessageFromServer) => {
    if (msg.type === 'user_stats_changed' && msg.user_id === userIdRef.current) {
      setRefreshKey((k) => k + 1)
    }
  }, [])

  useWebSocket(handleWSMessage)

  // ---- Render --------------------------------------------------------------

  // Loading state: skeleton sutil
  if (loading && !stats) {
    return (
      <div className="flex items-center gap-2 py-1 px-2 opacity-50 animate-pulse">
        <div className="w-6 h-6 bg-gray-800" />
        <div className="h-3 w-24 bg-gray-800" />
      </div>
    )
  }

  // Error state: renderiza fallback mínimo (só login + "?" se tem cache)
  if (error && !stats) {
    return (
      <div className="flex items-center gap-2 py-1 px-2 text-gray-600 text-xs">
        <span className="font-mono">[?]</span>
        <span>stats indisponíveis</span>
      </div>
    )
  }

  if (!stats) return null

  const tier = TIER_MAP[stats.tier]
  const isNovato = stats.tier === 'novato'

  // Placeholder visual reduzido para novato
  if (isNovato) {
    return (
      <div
        className="inline-flex items-center gap-2 py-1 px-2 text-xs text-gray-500
                   border border-gray-800 bg-gray-950/30"
        title={`${stats.login} — ${tier.label}`}
      >
        {/* Avatar miniatura */}
        <div className="w-5 h-5 flex items-center justify-center font-bold text-[10px] uppercase border border-gray-700">
          {stats.avatar_url ? (
            <img
              src={stats.avatar_url}
              alt={stats.login}
              className="w-full h-full object-cover"
              onError={(e) => {
                const t = e.currentTarget
                t.style.display = 'none'
                t.parentElement!.textContent = initials(stats.login)
              }}
            />
          ) : (
            initials(stats.login)
          )}
        </div>

        <span className="font-bold uppercase">{stats.login}</span>
        <span className="text-gray-600">•</span>
        <span>
          {tier.icon} {tier.label}
        </span>
      </div>
    )
  }

  // Cartão completo para iniciante / participante / veterano
  return (
    <div
      className={`inline-flex items-start gap-3 py-1.5 px-3 border ${tier.border} ${tier.bg}`}
      title={`${stats.login} — ${tier.label}`}
    >
      {/* Avatar */}
      <div className="w-8 h-8 flex items-center justify-center font-bold text-xs uppercase border border-white/20 shrink-0">
        {stats.avatar_url ? (
          <img
            src={stats.avatar_url}
            alt={stats.login}
            className="w-full h-full object-cover"
            onError={(e) => {
              const t = e.currentTarget
              t.style.display = 'none'
              t.parentElement!.textContent = initials(stats.login)
            }}
          />
        ) : (
          initials(stats.login)
        )}
      </div>

      {/* Info */}
      <div className="flex flex-col gap-0.5 min-w-0">
        {/* Linha 1: login + tier badge */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase text-white">
            {stats.login}
          </span>
          <span
            className={`text-[11px] font-bold uppercase tracking-wider border px-1.5 py-0.5 ${tier.color} ${tier.border}`}
          >
            {tier.icon} {tier.label}
          </span>
        </div>

        {/* Linha 2: stats */}
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>
            <strong className="text-gray-300">{stats.total_messages.toLocaleString('pt-BR')}</strong>{' '}
            {stats.total_messages === 1 ? 'mensagem' : 'mensagens'}
          </span>
          <span className="text-gray-600">•</span>
          <span>
            <strong className="text-gray-300">{stats.active_rooms}</strong>{' '}
            {stats.active_rooms === 1 ? 'sala ativa' : 'salas ativas'}
          </span>
        </div>
      </div>
    </div>
  )
}
