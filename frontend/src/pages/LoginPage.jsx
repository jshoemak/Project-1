import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Login failed' }))
        throw new Error(err.detail || 'Login failed')
      }
      const data = await res.json()
      localStorage.setItem('ct_token', data.token)
      navigate('/')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFirstRun = () => {
    // Bypass auth for first-time local setup — redirects to Profile to set email
    localStorage.setItem('ct_token', 'local_setup')
    navigate('/profile')
  }

  return (
    <div className="min-h-screen bg-navy-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center">
          <span className="text-accent font-bold text-2xl tracking-tight font-mono">
            &#9641; CONGRESS TRACKER
          </span>
          <p className="text-slate-500 text-sm mt-2">Sign in with your profile email</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Email Address</label>
            <input
              className="input-field w-full"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoFocus
            />
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-800 rounded px-3 py-2">
              <p className="text-coral-400 text-sm">{error}</p>
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full text-sm">
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <div className="text-center">
          <p className="text-xs text-slate-600 mb-2">First time using this app?</p>
          <button
            onClick={handleFirstRun}
            className="text-sm text-accent hover:underline"
          >
            Set up your profile →
          </button>
        </div>
      </div>
    </div>
  )
}
