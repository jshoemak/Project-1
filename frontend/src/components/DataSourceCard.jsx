import { useState } from 'react'
import { api } from '../hooks/useApi'

export function FreeSourceCard({ source }) {
  return (
    <div className="card p-4 flex items-start justify-between">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <p className="font-medium text-slate-200">{source.label}</p>
          <span className="text-xs bg-emerald-900 text-emerald-400 px-2 py-0.5 rounded-full">
            ✓ Connected
          </span>
        </div>
        <p className="text-sm text-slate-500">{source.description}</p>
      </div>
    </div>
  )
}

export function PremiumSourceCard({ source, onConnected }) {
  const [open, setOpen] = useState(false)
  const [key, setKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [connected, setConnected] = useState(source.connected)

  const save = async () => {
    if (!key.trim()) { setError('API key is required'); return }
    setLoading(true)
    setError(null)
    try {
      await api.post(`/sources/${source.name}/connect`, { api_key: key.trim() })
      setConnected(true)
      setOpen(false)
      onConnected?.()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card p-4">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <p className="font-medium text-slate-200">{source.label}</p>
            <span className="text-xs text-slate-500 bg-navy-700 px-2 py-0.5 rounded">
              {source.price}
            </span>
            {connected && (
              <span className="text-xs bg-emerald-900 text-emerald-400 px-2 py-0.5 rounded-full">
                ✓ Connected
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500">{source.description}</p>
        </div>
        {!connected && (
          <button
            onClick={() => setOpen((x) => !x)}
            className="btn-primary text-xs ml-4 shrink-0"
          >
            Connect
          </button>
        )}
        {connected && (
          <button
            onClick={() => setOpen((x) => !x)}
            className="btn-ghost text-xs ml-4 shrink-0"
          >
            Update Key
          </button>
        )}
      </div>

      {open && (
        <div className="mt-3 pt-3 border-t border-navy-700">
          {error && <p className="text-coral-400 text-xs mb-2">{error}</p>}
          <div className="flex gap-2">
            <input
              type="password"
              className="input-field text-sm font-mono"
              placeholder="Paste API key…"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && save()}
            />
            <button onClick={save} disabled={loading} className="btn-primary text-sm shrink-0">
              {loading ? '…' : 'Save'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
