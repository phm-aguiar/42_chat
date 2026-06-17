import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/auth'

export default function Callback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()

  useEffect(() => {
    const code = searchParams.get('code')
    if (!code) {
      navigate('/')
      return
    }

    // Trocar code por JWT via backend
    fetch(`/api/auth/42/callback?code=${encodeURIComponent(code)}`)
      .then(res => {
        if (!res.ok) throw new Error('OAuth failed')
        return res.json()
      })
      .then(data => {
        login(data.token, data.user)
        navigate('/chat')
      })
      .catch(err => {
        console.error('OAuth callback error:', err)
        navigate('/')
      })
  }, [searchParams, navigate, login])

  return (
    <div className="min-h-screen bg-black dot-grid flex items-center justify-center">
      <div className="text-center">
        <div className="animate-pulse text-lime text-2xl font-bold uppercase tracking-widest">
          Autenticando...
        </div>
        <p className="text-gray-500 mt-4 text-sm">Conectando à intra da 42</p>
      </div>
    </div>
  )
}
