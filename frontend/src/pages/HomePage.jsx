import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { formatCurrency } from '../utils/format'
import PerformanceChart from '../components/PerformanceChart'
import HoldingRow from '../components/HoldingRow'
import AddHoldingForm from '../components/AddHoldingForm'

export default function HomePage() {
  const { data: holdings, loading, refetch } = useApi('/holdings')
  const { data: signals } = useApi('/signals?min_score=60')
  const [showAdd, setShowAdd] = useState(false)
  const [prefill, setPrefill] = useState({})
  const location = useLocation()

  // Open add form pre-filled when navigated from signals
  useEffect(() => {
    if (location.state?.prefill) {
      setPrefill(location.state.prefill)
      setShowAdd(true)
      // Clear state so refresh doesn't re-open
      window.history.replaceState({}, '')
    }
  }, [location.state])

  const highSignals = signals?.filter((s) => s.conviction_score >= 80) ?? []
  const allHoldings = holdings ?? []

  const handleAdded = () => {
    setShowAdd(false)
    setPrefill({})
    refetch()
  }

  const handleDelete = () => refetch()

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
      {/* Signal indicator */}
      {highSignals.length > 0 && (
        <Link
          to="/signals"
          className="inline-flex items-center gap-2 text-sm text-amber-400 hover:text-amber-300 transition-colors"
        >
          <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
          {highSignals.length} high-conviction trade signal{highSignals.length !== 1 ? 's' : ''} detected
          <span className="text-slate-500">→</span>
        </Link>
      )}

      {/* Portfolio value header */}
      <PortfolioHeader holdings={allHoldings} />

      {/* Performance chart */}
      <PerformanceChart />

      {/* Holdings list */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="section-label">Holdings</p>
          <button
            onClick={() => { setShowAdd((x) => !x); if (showAdd) setPrefill({}) }}
            className="btn-primary text-xs"
          >
            {showAdd ? 'Cancel' : '+ Add Position'}
          </button>
        </div>

        {showAdd && (
          <AddHoldingForm
            prefill={prefill}
            onAdded={handleAdded}
            onCancel={() => { setShowAdd(false); setPrefill({}) }}
          />
        )}

        {loading ? (
          <div className="text-slate-600 text-sm py-8 text-center">Loading…</div>
        ) : allHoldings.length === 0 ? (
          <div className="card p-8 text-center">
            <p className="text-slate-500 mb-3">No holdings yet.</p>
            <button onClick={() => setShowAdd(true)} className="btn-primary text-sm">
              Add Your First Position
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {allHoldings.map((h) => (
              <HoldingRow key={h.id} holding={h} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function PortfolioHeader({ holdings }) {
  const totalCost = holdings.reduce((s, h) => s + h.shares * h.avg_cost, 0)
  return (
    <div>
      <p className="section-label">Total Portfolio</p>
      <p className="font-mono text-4xl font-bold text-slate-100">
        {totalCost > 0 ? formatCurrency(totalCost) : '—'}
      </p>
      <p className="text-xs text-slate-500 mt-1">Cost basis · Live prices load in holding rows</p>
    </div>
  )
}
