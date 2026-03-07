import { useState } from 'react'
import { useApi, api } from '../hooks/useApi'
import SignalCard from '../components/SignalCard'

const FILTERS = [
  { label: 'All', min: 0 },
  { label: '60+', min: 60 },
  { label: '80+', min: 80 },
]

export default function SignalsPage() {
  const [minScore, setMinScore] = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const { data, loading, error, refetch } = useApi(`/signals?min_score=${minScore}`, [minScore])

  const signals = data ?? []

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await api.post('/refresh', {})
      await refetch()
    } catch (e) {
      alert('Refresh failed: ' + e.message)
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Trade Signals</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Conviction-scored from congressional disclosures
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Score filter */}
          <div className="flex gap-1 bg-navy-800 rounded-lg p-1">
            {FILTERS.map((f) => (
              <button
                key={f.label}
                onClick={() => setMinScore(f.min)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  minScore === f.min
                    ? 'bg-accent text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn-ghost text-xs"
          >
            {refreshing ? '⟳ Refreshing…' : '⟳ Refresh'}
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-amber-500 inline-block" /> 80+ High conviction
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-accent inline-block" /> 60–79 Moderate
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-slate-600 inline-block" /> &lt;60 Low
        </span>
      </div>

      {/* Signals list */}
      {loading ? (
        <div className="text-center text-slate-600 py-12 text-sm">Loading signals…</div>
      ) : error ? (
        <div className="text-center text-coral-400 py-12 text-sm">Error: {error}</div>
      ) : signals.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-slate-500 mb-2">No signals found.</p>
          <p className="text-xs text-slate-600">
            Run <code className="bg-navy-700 px-1 rounded">python initial_data_pull.py</code> to populate data.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {signals.map((s) => (
            <SignalCard key={s.ticker} signal={s} />
          ))}
        </div>
      )}
    </div>
  )
}
