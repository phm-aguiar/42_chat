import { useNavigate, useSearchParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuthStore } from '../stores/auth'

const FORTY_TWO_REDIRECT_URI = import.meta.env.VITE_42_REDIRECT_URI || `${window.location.origin}/callback`
const FORTY_TWO_CLIENT_ID = import.meta.env.VITE_42_CLIENT_ID || 'dev-client-id'
const FORTY_TWO_AUTH_URL = `https://api.intra.42.fr/oauth/authorize?client_id=${FORTY_TWO_CLIENT_ID}&redirect_uri=${encodeURIComponent(FORTY_TWO_REDIRECT_URI)}&response_type=code`
const DEV_MODE = import.meta.env.VITE_DEV_MODE === 'true'
const API_URL = import.meta.env.VITE_API_URL || ''

export default function Login() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isAuthenticated, login } = useAuthStore()
  const [devLoginInput, setDevLoginInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Se chegou com ?code= na URL (redirect OAuth2 sem /callback), redireciona
  useEffect(() => {
    const code = searchParams.get('code')
    if (code) {
      navigate(`/callback?code=${encodeURIComponent(code)}`, { replace: true })
    }
  }, [searchParams, navigate])

  // Redireciona pro chat se já autenticado
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat')
    }
  }, [isAuthenticated, navigate])

  const handleDevLogin = async () => {
    const loginName = devLoginInput.trim() || 'marvin'
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API_URL}/api/auth/dev/login?login=${encodeURIComponent(loginName)}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      login(data.token, data.user)
      navigate('/chat')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black dot-grid flex items-center justify-center">
      <div className="card-42 p-12 max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-6xl font-black text-white tracking-tighter">
            42<span className="text-lime">_</span>CHAT
          </h1>
          <p className="text-gray-500 text-sm mt-2 uppercase tracking-widest">
            Campus São Paulo
          </p>
        </div>

        <p className="text-gray-400 text-sm mb-8 leading-relaxed">
          Comunicação em tempo real para a comunidade 42.
          Login exclusivo via OAuth2 da intra.
        </p>

        <a href={FORTY_TWO_AUTH_URL} className="btn-42 block text-center w-full">
          Login com 42
        </a>

        {DEV_MODE && (
          <div className="mt-6 pt-6 border-t border-gray-800">
            <p className="text-cyano text-xs uppercase tracking-wider mb-3">Dev Mode</p>
            <div className="flex gap-2">
              <input
                type="text"
                value={devLoginInput}
                onChange={(e) => setDevLoginInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleDevLogin()}
                placeholder="marvin"
                className="flex-1 bg-gray-900 border-2 border-gray-700 text-white px-3 py-2 text-sm font-mono outline-none focus:border-cyano"
              />
              <button
                onClick={handleDevLogin}
                disabled={loading}
                className="btn-42 px-4 py-2 text-sm whitespace-nowrap"
              >
                {loading ? '...' : 'Dev Login'}
              </button>
            </div>
            {error && <p className="text-magenta text-xs mt-2">{error}</p>}
          </div>
        )}

        <div className="mt-8 pt-8 border-t-2 border-white">
          <p className="text-gray-600 text-xs uppercase tracking-wider">
            v0.1.0 MVP &middot; ~300 alunos
          </p>
        </div>
      </div>
    </div>
  )
}
