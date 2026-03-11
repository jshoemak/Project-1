import { useState, useEffect } from 'react'
import { useApi, api } from '../hooks/useApi'

const DEFAULT_WEIGHTS = {
  congressional_vol: 20,
  committee_relevance: 20,
  bipartisan: 15,
  contract_correlation: 15,
  donation_alignment: 10,
  direction_consensus: 10,
  freshness: 10,
}

const WEIGHT_LABELS = {
  congressional_vol: 'Congressional Volume',
  committee_relevance: 'Committee Relevance',
  bipartisan: 'Bipartisan Activity',
  contract_correlation: 'Contract Correlation',
  donation_alignment: 'Donation Alignment',
  direction_consensus: 'Direction Consensus',
  freshness: 'Freshness',
}

export default function ProfilePage() {
  const { data: profile, loading } = useApi('/profile')
  const [form, setForm] = useState({ name: '', email: '' })
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (profile) {
      setForm({ name: profile.name || '', email: profile.email || '' })
      setWeights({ ...DEFAULT_WEIGHTS, ...profile.weights })
    }
  }, [profile])

  const totalWeight = Object.values(weights).reduce((s, v) => s + Number(v), 0)

  const setWeight = (key) => (e) => {
    setWeights((w) => ({ ...w, [key]: Number(e.target.value) }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      // Normalize weights to sum to 100
      const normalizedWeights = {}
      const keys = Object.keys(weights)
      const total = keys.reduce((s, k) => s + Number(weights[k]), 0)
      keys.forEach((k) => {
        normalizedWeights[k] = total > 0 ? Math.round((Number(weights[k]) / total) * 100) : 0
      })
      await api.put('/profile', { name: form.name, email: form.email, weights: normalizedWeights })
      setWeights(normalizedWeights)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="max-w-3xl mx-auto px-4 py-6 text-slate-500 text-sm">Loading…</div>
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Profile</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Your identity and signal scoring preferences
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* User info */}
        <div className="card p-5 space-y-4">
          <p className="section-label">Account Information</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Full Name</label>
              <input
                className="input-field w-full"
                placeholder="John Smith"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Email Address</label>
              <input
                className="input-field w-full"
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              />
              <p className="text-xs text-slate-600 mt-1">
                Used to authenticate your remote sessions
              </p>
            </div>
          </div>
        </div>

        {/* Signal weights */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <p className="section-label">Signal Weighting</p>
            <span className={`text-xs font-mono ${totalWeight === 100 ? 'text-emerald-400' : 'text-amber-400'}`}>
              Total: {totalWeight}% {totalWeight !== 100 && '(auto-normalized on save)'}
            </span>
          </div>
          <p className="text-xs text-slate-500">
            Adjust how each factor contributes to the conviction score. Values are normalized to 100% on save.
          </p>
          <div className="space-y-4">
            {Object.keys(DEFAULT_WEIGHTS).map((key) => (
              <div key={key}>
                <div className="flex justify-between mb-1">
                  <label className="text-sm text-slate-300">{WEIGHT_LABELS[key]}</label>
                  <span className="text-sm font-mono text-accent">{weights[key]}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="50"
                  step="1"
                  value={weights[key]}
                  onChange={setWeight(key)}
                  className="w-full h-1.5 bg-navy-700 rounded-full appearance-none cursor-pointer accent-blue-500"
                />
              </div>
            ))}
          </div>
        </div>

        {error && <p className="text-coral-400 text-sm">{error}</p>}

        <div className="flex items-center gap-3">
          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? 'Saving…' : 'Save Profile'}
          </button>
          {saved && (
            <span className="text-emerald-400 text-sm">✓ Saved successfully</span>
          )}
        </div>
      </form>
    </div>
  )
}
